import logging
import uuid

from sqlalchemy import Column, ForeignKey, String, orm, event
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from walkoff.appgateway import get_app_action, is_app_action_bound
from walkoff.appgateway.actionresult import ActionResult
from walkoff.appgateway.validator import validate_app_action_parameters
from walkoff.events import WalkoffEvent
from walkoff.executiondb import Execution_Base
from walkoff.executiondb.argument import Argument
from walkoff.executiondb.executionelement import ExecutionElement
from walkoff.helpers import format_exception_message
from walkoff.appgateway.apiutil import get_app_action_api, UnknownApp, UnknownAppAction, InvalidArgument

logger = logging.getLogger(__name__)


class ChildWorkflow(ExecutionElement, Execution_Base):
    __tablename__ = 'child_workflow'
    parent_workflow_id = Column(UUIDType(binary=False), ForeignKey('workflow.id'))
    child_workflow_id = Column(UUIDType(binary=False))
    arguments = relationship('Argument', cascade='all, delete, delete-orphan')
    position = relationship('Position', uselist=False, cascade='all, delete-orphan')
    children = ('arguments', )

    def __init__(self, child_workflow_id, id=None, arguments=None, position=None):
        """Initializes a new ChildWorkflow object
        Args:
            child_workflow_id (UUID): The workflow ID which should be executed
            id (str|UUID, optional): Optional UUID to pass into the Action. Must be UUID object or valid UUID string.
                Defaults to None.

            arguments (list[Argument], optional): A list of Argument objects which are used for the starting action of the
                workflow.
            position (Position, optional): Position of the Child Workflow object
        """
        print(locals())
        ExecutionElement.__init__(self, id)
        self.child_workflow_id = child_workflow_id
        self.arguments = arguments or []
        self.position = position
        self.validate()
        self._output = None

    def get_output(self):
        return self._output

    def execute(self, accumulator, db):
        from walkoff.executiondb.workflow import Workflow
        workflow = db.session.query(Workflow).filter_by(id=self.child_workflow_id).first()
        arguments = [Argument(arg.name, value=arg.get_value(accumulator)) for arg in self.arguments]
        result = workflow.execute(start_arguments=arguments)
        self._output = result
        return result


@event.listens_for(ChildWorkflow, 'before_update')
def validate_before_update(mapper, connection, target):
    # TODO: Validate that the workflow exists
    target.validate()