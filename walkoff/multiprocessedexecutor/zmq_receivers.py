import logging
import json

import gevent
import zmq.green as zmq
from flask import Flask
from redis import Redis

import walkoff.config
from walkoff.events import WalkoffEvent
from walkoff.multiprocessedexecutor.protoconverter import ProtobufWorkflowResultsConverter
from walkoff.server import context

logger = logging.getLogger(__name__)


class ZmqWorkflowResultsReceiver(object):
    def __init__(self, message_converter=ProtobufWorkflowResultsConverter, current_app=None):
        """Initialize a Receiver object, which will receive callbacks from the ExecutionElements.

        Args:
            current_app (Flask.App, optional): The current Flask app. If the Receiver is not started separately,
                then the current_app must be included in the init. Otherwise, it should not be included.
            message_converter (WorkflowResultsConverter): Class to convert workflow results
        """
        import walkoff.server.workflowresults  # Need this import

        config = walkoff.config.Config()
        config.load_env_vars()

        self.redis_cache = Redis(host=config.CACHE["host"], port=config.CACHE["port"])

        self.workflow_results_pubsub = self.redis_cache.pubsub()
        self.workflow_results_pubsub.subscribe("workflow-results")
        self.action_results_pubsub = self.redis_cache.pubsub()
        self.action_results_pubsub.subscribe("action-results")
        # ctx = zmq.Context.instance()
        # self.message_converter = message_converter
        self.thread_exit = False
        self.workflows_executed = 0
        #
        # self.results_sock = ctx.socket(zmq.PULL)
        # self.results_sock.curve_secretkey = walkoff.config.Config.SERVER_PRIVATE_KEY
        # self.results_sock.curve_publickey = walkoff.config.Config.SERVER_PUBLIC_KEY
        # self.results_sock.curve_server = True
        # self.results_sock.bind(walkoff.config.Config.ZMQ_RESULTS_ADDRESS)
        #
        # if current_app is None:
        #     self.current_app = Flask(__name__)
        #     self.current_app.config.from_object(walkoff.config.Config)
        #     self.current_app.running_context = context.Context(init_all=False)
        # else:
        self.current_app = current_app

    def receive_results(self):
        """Keep receiving results from execution elements over a ZMQ socket, and trigger the callbacks"""
        while True:
            if self.thread_exit:
                break
            # message_bytes = self.results_sock.recv(zmq.NOBLOCK)
            workflow_results_message = self.workflow_results_pubsub.get_message(ignore_subscribe_messages=True)  # ToDo: ignore sub/unsub?
            if workflow_results_message:
                print(workflow_results_message)
                with self.current_app.app_context():
                    self._send_callback(workflow_results_message)

            action_results_message = self.action_results_pubsub.get_message(ignore_subscribe_messages=True)
            if action_results_message:
                with self.current_app.app_context():
                    self._send_callback(action_results_message.get("data", ''))

            gevent.sleep(0.1)

        return

    def _send_callback(self, message):
        event, sender, data = self._message_to_event_callback(message)

        if sender is not None and event is not None:
            if self.current_app:
                with self.current_app.app_context():
                    event.send(sender, data=data)
            else:
                event.send(sender, data=data)
            if event in [WalkoffEvent.WorkflowShutdown, WalkoffEvent.WorkflowAborted]:
                self._increment_execution_count()

    def _message_to_event_callback(self, message):
        message = json.loads(message)
        event = WalkoffEvent.get_event_from_name(message.get("status", None))

        if event is not None:
            # data = ProtobufWorkflowResultsConverter._format_callback_data(event, message, sender)
            return event, message, message
        else:
            logger.error('Unknown callback {} sent'.format(event))
            return None, None, None

    def _increment_execution_count(self):
        self.workflows_executed += 1
