import logging
from jaeger_client import Config
from jaeger_client.reporter import (
    Reporter,
    CompositeReporter,
    NullReporter
)

from jaeger_client.sampler import RemoteControlledSampler
from jaeger_client.throttler import RemoteThrottler
from jaeger_logger.reporter import LoggerTracerReporter


default_logger = logging.getLogger('tracer')


class LoggerTraceConfig(Config):

    def initialize_tracer(self, io_loop=None, logger=LoggerTracerReporter):
        """
        Initialize Jaeger Tracer based on the passed `jaeger_client.Config`.
        Save it to `opentracing.tracer` global variable.
        Only the first call to this method has any effect.
        """

        with Config._initialized_lock:
            if Config._initialized:
                logger.warn('Jaeger tracer already initialized, skipping')
                return
            Config._initialized = True

        tracer = self.new_tracer(logger, io_loop)

        self._initialize_global_tracer(tracer=tracer)
        return tracer

    def new_tracer(self, logger, io_loop=None):
        """
        Create a new Jaeger Tracer based on the passed `jaeger_client.Config`.
        """
        channel = self._create_local_agent_channel(io_loop=io_loop)
        sampler = self.sampler
        if not sampler:
            sampler = RemoteControlledSampler(
                channel=channel,
                service_name=self.service_name,
                logger=default_logger,
                metrics_factory=self._metrics_factory,
                error_reporter=self.error_reporter,
                sampling_refresh_interval=self.sampling_refresh_interval,
                max_operations=self.max_operations)
        default_logger.info('Using sampler %s', sampler)

        reporter = Reporter(
            channel=channel,
            queue_capacity=self.reporter_queue_size,
            batch_size=self.reporter_batch_size,
            flush_interval=self.reporter_flush_interval,
            logger=default_logger,
            metrics_factory=self._metrics_factory,
            error_reporter=self.error_reporter)

        if self.logging:
            reporter = CompositeReporter(
                reporter, logger)

        if not self.throttler_group() is None:
            throttler = RemoteThrottler(
                channel,
                self.service_name,
                refresh_interval=self.throttler_refresh_interval,
                logger=default_logger,
                metrics_factory=self._metrics_factory,
                error_reporter=self.error_reporter)
        else:
            throttler = None

        return self.create_tracer(
            reporter=reporter,
            sampler=sampler,
            throttler=throttler,
        )
