"""
Experiment scheduler and execution engine.

This module implements the core scheduling logic for managing experiment
queues, parameter generation, and execution coordination.
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from queue import PriorityQueue, Queue
from typing import Dict, List, Optional, Set
import uuid

from .interfaces import IExperimentExecutor, IProgressMonitor
from .models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    SweepConfiguration,
    SweepExecution,
)


logger = logging.getLogger(__name__)


class ExperimentScheduler:
    """
    Central orchestration engine that manages experiment queues,
    parameter generation, and execution coordination.
    """
    
    def __init__(
        self,
        executors: List[IExperimentExecutor],
        progress_monitor: Optional[IProgressMonitor] = None,
        max_concurrent_experiments: int = 4,
    ):
        """
        Initialize the experiment scheduler.
        
        Args:
            executors: List of available experiment executors
            progress_monitor: Optional progress monitor for tracking
            max_concurrent_experiments: Maximum concurrent experiments
        """
        self.executors = executors
        self.progress_monitor = progress_monitor
        self.max_concurrent_experiments = max_concurrent_experiments
        
        # Execution tracking
        self.active_executions: Dict[str, SweepExecution] = {}
        self.experiment_queue = PriorityQueue()
        self.result_queue = Queue()
        
        # Thread management
        self.executor_pool = ThreadPoolExecutor(max_workers=max_concurrent_experiments)
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Statistics
        self.total_experiments_executed = 0
        self.total_execution_time = 0.0
        self.total_cost = 0.0
    
    def schedule_sweep(self, config: SweepConfiguration) -> SweepExecution:
        """
        Schedule a parameter sweep for execution.
        
        Args:
            config: Sweep configuration defining parameters and objectives
            
        Returns:
            SweepExecution object for tracking progress
        """
        logger.info(f"Scheduling sweep: {config.name}")
        
        # Create sweep execution
        execution = SweepExecution(
            execution_id=str(uuid.uuid4()),
            sweep_config=config,
            status="scheduled",
            start_time=datetime.now(),
        )
        
        # Generate experiments from parameter combinations
        experiments = self._generate_experiments(config)
        execution.experiments = experiments
        
        # Store execution
        self.active_executions[execution.execution_id] = execution
        
        # Queue experiments for execution
        for experiment in experiments:
            # Priority is negative because PriorityQueue is min-heap
            self.experiment_queue.put((-experiment.priority, experiment))
        
        # Start scheduler if not running
        if not self.running:
            self.start_scheduler()
        
        # Update execution status to running
        execution.status = "running"
        
        # Start progress monitoring
        if self.progress_monitor:
            self.progress_monitor.start_monitoring(execution.execution_id)
        
        logger.info(f"Scheduled {len(experiments)} experiments for sweep {config.name}")
        return execution
    
    def _generate_experiments(self, config: SweepConfiguration) -> List[Experiment]:
        """
        Generate experiments from sweep configuration.
        
        Args:
            config: Sweep configuration
            
        Returns:
            List of experiments to execute
        """
        experiments = []
        parameter_combinations = config.generate_parameter_combinations()
        
        for i, params in enumerate(parameter_combinations):
            for project_path in config.project_paths:
                experiment = Experiment(
                    experiment_id=f"{config.name}_{project_path.split('/')[-1]}_{i}",
                    project_path=project_path,
                    parameters=params,
                    objectives=config.objectives,
                    priority=1.0,  # Default priority, can be adjusted by optimizer
                )
                
                # Estimate duration and cost using available executors
                self._estimate_experiment_resources(experiment)
                experiments.append(experiment)
        
        return experiments
    
    def _estimate_experiment_resources(self, experiment: Experiment) -> None:
        """
        Estimate duration and cost for an experiment using available executors.
        
        Args:
            experiment: Experiment to estimate
        """
        best_duration = None
        best_cost = None
        
        for executor in self.executors:
            if executor.can_execute(experiment):
                try:
                    duration = executor.estimate_duration(experiment)
                    cost = executor.estimate_cost(experiment)
                    
                    if best_duration is None or duration < best_duration:
                        best_duration = duration
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        
                except Exception as e:
                    logger.warning(f"Failed to estimate resources for {experiment.experiment_id}: {e}")
        
        experiment.estimated_duration = best_duration
        experiment.estimated_cost = best_cost
    
    def start_scheduler(self) -> None:
        """Start the experiment scheduler thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Experiment scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the experiment scheduler thread."""
        if not self.running:
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        
        # Shutdown executor pool
        self.executor_pool.shutdown(wait=True)
        logger.info("Experiment scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop that processes experiment queue."""
        logger.info("Scheduler loop started")
        
        active_futures = set()
        
        while self.running or not self.experiment_queue.empty() or active_futures:
            try:
                # Submit new experiments if we have capacity
                while (len(active_futures) < self.max_concurrent_experiments and 
                       not self.experiment_queue.empty()):
                    
                    try:
                        priority, experiment = self.experiment_queue.get_nowait()
                        future = self.executor_pool.submit(self._execute_experiment, experiment)
                        active_futures.add(future)
                        logger.debug(f"Submitted experiment {experiment.experiment_id}")
                    except Exception as e:
                        logger.error(f"Failed to submit experiment: {e}")
                
                # Process completed experiments
                completed_futures = set()
                for future in active_futures:
                    if future.done():
                        completed_futures.add(future)
                        try:
                            result = future.result()
                            self._process_experiment_result(result)
                        except Exception as e:
                            logger.error(f"Experiment execution failed: {e}")
                
                # Remove completed futures
                active_futures -= completed_futures
                
                # Brief sleep to prevent busy waiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(1.0)
        
        logger.info("Scheduler loop finished")
    
    def _execute_experiment(self, experiment: Experiment) -> ExperimentResult:
        """
        Execute a single experiment using the best available executor.
        
        Args:
            experiment: Experiment to execute
            
        Returns:
            ExperimentResult containing execution results
        """
        logger.info(f"Executing experiment {experiment.experiment_id}")
        start_time = time.time()
        
        # Find the best executor for this experiment
        best_executor = None
        best_cost = float('inf')
        
        for executor in self.executors:
            if executor.can_execute(experiment):
                try:
                    cost = executor.estimate_cost(experiment)
                    if cost < best_cost:
                        best_cost = cost
                        best_executor = executor
                except Exception as e:
                    logger.warning(f"Failed to estimate cost with {executor}: {e}")
        
        if best_executor is None:
            # Create failed result
            execution_time = time.time() - start_time
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                project_name=experiment.project_path.split('/')[-1],
                parameters=experiment.parameters,
                metrics={},
                execution_time=execution_time,
                status=ExperimentStatus.FAILED,
                error_message="No suitable executor found",
            )
        
        try:
            # Execute the experiment
            result = best_executor.execute(experiment)
            result.execution_time = time.time() - start_time
            
            # Update statistics
            self.total_experiments_executed += 1
            self.total_execution_time += result.execution_time
            if result.cost:
                self.total_cost += result.cost
            
            logger.info(f"Completed experiment {experiment.experiment_id} in {result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Experiment {experiment.experiment_id} failed: {e}")
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                project_name=experiment.project_path.split('/')[-1],
                parameters=experiment.parameters,
                metrics={},
                execution_time=execution_time,
                status=ExperimentStatus.FAILED,
                error_message=str(e),
            )
    
    def _process_experiment_result(self, result: ExperimentResult) -> None:
        """
        Process a completed experiment result.
        
        Args:
            result: Completed experiment result
        """
        # Find the execution this result belongs to
        execution = None
        for exec_id, sweep_exec in self.active_executions.items():
            if any(exp.experiment_id == result.experiment_id for exp in sweep_exec.experiments):
                execution = sweep_exec
                break
        
        if execution is None:
            logger.warning(f"Could not find execution for result {result.experiment_id}")
            return
        
        # Add result to execution
        execution.results.append(result)
        
        # Update total cost
        if result.cost:
            execution.total_cost += result.cost
        
        # Update progress monitoring
        if self.progress_monitor:
            self.progress_monitor.update_progress(
                execution.execution_id,
                execution.progress,
                execution.results
            )
        
        # Check if execution is complete
        if len(execution.results) >= len(execution.experiments):
            execution.status = "completed"
            execution.end_time = datetime.now()
            
            if self.progress_monitor:
                self.progress_monitor.stop_monitoring(execution.execution_id)
            
            logger.info(f"Sweep execution {execution.execution_id} completed")
            logger.info(f"Success rate: {execution.success_rate:.1f}%")
            logger.info(f"Total cost: ${execution.total_cost:.2f}")
    
    def get_execution_status(self, execution_id: str) -> Optional[SweepExecution]:
        """
        Get the status of a sweep execution.
        
        Args:
            execution_id: ID of the execution to check
            
        Returns:
            SweepExecution object or None if not found
        """
        return self.active_executions.get(execution_id)
    
    def pause_execution(self, execution_id: str) -> bool:
        """
        Pause a sweep execution.
        
        Args:
            execution_id: ID of the execution to pause
            
        Returns:
            True if successfully paused
        """
        execution = self.active_executions.get(execution_id)
        if execution and execution.status == "running":
            execution.status = "paused"
            logger.info(f"Paused execution {execution_id}")
            return True
        return False
    
    def resume_execution(self, execution_id: str) -> bool:
        """
        Resume a paused sweep execution.
        
        Args:
            execution_id: ID of the execution to resume
            
        Returns:
            True if successfully resumed
        """
        execution = self.active_executions.get(execution_id)
        if execution and execution.status == "paused":
            execution.status = "running"
            logger.info(f"Resumed execution {execution_id}")
            return True
        return False
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a sweep execution.
        
        Args:
            execution_id: ID of the execution to cancel
            
        Returns:
            True if successfully cancelled
        """
        execution = self.active_executions.get(execution_id)
        if execution and execution.status in ["running", "paused", "scheduled"]:
            execution.status = "cancelled"
            execution.end_time = datetime.now()
            
            if self.progress_monitor:
                self.progress_monitor.stop_monitoring(execution_id)
            
            logger.info(f"Cancelled execution {execution_id}")
            return True
        return False
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get scheduler statistics.
        
        Returns:
            Dictionary containing scheduler statistics
        """
        return {
            "total_experiments_executed": self.total_experiments_executed,
            "total_execution_time": self.total_execution_time,
            "total_cost": self.total_cost,
            "active_executions": len(self.active_executions),
            "queue_size": self.experiment_queue.qsize(),
            "average_execution_time": (
                self.total_execution_time / self.total_experiments_executed
                if self.total_experiments_executed > 0 else 0.0
            ),
        }