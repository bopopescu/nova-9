import json
import traceback
from oslo_log import log as logging

from nova.api.openstack.compute.schemas import disk_qos
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova.policies import disk_qos as diskqos_policies

LOG = logging.getLogger(__name__)

ALIAS = "diskqos"


class DiskQosController(wsgi.Controller):

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(DiskQosController, self).__init__()

    def _get_ics_session(self):
        if self.ics_manager:
            return True
        try:
            from ics_sdk import session
            self.ics_manager = session.get_session()
            return True
        except:
            self.ics_manager = None
            return False

    # Define support for GET on a collection
    def index(self, req):
        data = {'param': 'test diskqos'}
        return data

    @extensions.expected_errors(404)
    def show(self, req, id):
        """Return detailed information disk qos about a specific server.
        :param req: `wsgi.Request` object
        :param id: Server identifier
        """
        context = req.environ['nova.context']
        context.can(diskqos_policies.BASE_POLICY_NAME)
        vm_id = id
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            disk_qos = self.ics_manager.vm.get_disk_qos(vm_id)
            LOG.info('--Get disk qos of vm from ICS-- : ' + json.dumps(disk_qos))
            return dict({'vmid':vm_id, 'disk_qos':disk_qos})
        except Exception as e:
            LOG.error('Error to get disk qos from ICS : ' + traceback.format_exc())
            return dict(disk_qos=[], error=e.message)

    @extensions.expected_errors((400, 403, 404, 409))
    @validation.schema(disk_qos.diskqos)
    def create(self, req, body):
        context = req.environ['nova.context']
        context.can(diskqos_policies.BASE_POLICY_NAME)
        vm_id = body.get('vmid')
        LOG.debug('Receive ICM request to set disk qos of vm "%s", '
                  'parameter is "%s".' % (vm_id, json.dumps(body)))
        # connect ICS
        if not self._get_ics_session():
            return dict(result='fail', error='CANNOT_CONNECT_ICS')
        # begin to set or update
        disk_qos = {}
        disk_qos["enabled"] = body['disk_qos']['enabled']
        disk_qos["readBps"] = body['disk_qos']['readBps']
        disk_qos["writeBps"] = body['disk_qos']['writeBps']
        disk_qos["readIops"] = body['disk_qos']['readIops']
        disk_qos["writeIops"] = body['disk_qos']['writeIops']
        disk_qos["totalBps"] = body['disk_qos']['totalBps']
        disk_qos["totalIops"] = body['disk_qos']['totalIops']
        try:
            task = self.ics_manager.vm.set_disk_qos(vm_id,disk_qos)
            return dict({'result':'success'})
        except Exception as e:
            LOG.error('Error to set disk qos of vm "%s", data is "%s", '
                      'error message is "%s".'
                      % (vm_id, json.dumps(body), e.message))
            return dict(result='fail', error=e.message)

class DiskQos(extensions.V21APIExtensionBase):

    name = "DiskQos"
    alias = ALIAS
    version = 1

    def get_resources(self):
        resources = [extensions.ResourceExtension(ALIAS, DiskQosController())]
        return resources

    def get_controller_extensions(self):
        return []

