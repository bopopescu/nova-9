import json
import traceback
from oslo_log import log as logging

from nova.api.openstack.compute.schemas import cpu_qos
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova.policies import cpu_qos as cpuqos_policies

LOG = logging.getLogger(__name__)

ALIAS = "cpuqos"


class CpuQosController(wsgi.Controller):

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(CpuQosController, self).__init__()

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
        data = {'param': 'test cpuqos'}
        return data

    @extensions.expected_errors(404)
    def show(self, req, id):
        """Return detailed information cpu qos about a specific server.
        :param req: `wsgi.Request` object
        :param id: Server identifier
        """
        context = req.environ['nova.context']
        context.can(cpuqos_policies.BASE_POLICY_NAME)
        vm_id = id
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            vcpu_qos = self.ics_manager.vm.get_vcpu_qos(vm_id)
            vm_info = self.ics_manager.vm.get_info(vm_id)
            LOG.debug("vm_info:%s",vm_info)
            hostId = ""
            hostId = vm_info['hostId']
            LOG.debug("host_id:%s",hostId)
            cpuCore = int(vm_info['cpuCore'])
            host_info = self.ics_manager.host.get_host(hostId)
            LOG.debug("host_info:%s",host_info)
            cpuHz = float(host_info['cpuTotalHz']) / float(host_info['logicalProcessor'])
            vcpu_qos_max = 1000 * cpuHz * cpuCore
            LOG.info('--Get cpu qos of vm from ICS-- : ' + json.dumps(vcpu_qos))
            return dict({'vmid':vm_id, 'vcpu_qos':vcpu_qos, 'vcpu_qos_max':vcpu_qos_max})
        except Exception as e:
            LOG.error('Error to get cpu qos from ICS : ' + traceback.format_exc())
            return dict(vcpu_qos=[], error=e.message)

    @extensions.expected_errors((400, 403, 404, 409))
    @validation.schema(cpu_qos.cpuqos)
    def create(self, req, body):
        context = req.environ['nova.context']
        context.can(cpuqos_policies.BASE_POLICY_NAME)
        vm_id = body.get('vmid')
        LOG.debug('Receive ICM request to set cpu qos of vm "%s", '
                  'parameter is "%s".' % (vm_id, json.dumps(body)))
        # connect ICS
        if not self._get_ics_session():
            return dict(result='fail', error='CANNOT_CONNECT_ICS')
        # begin to set or update
        #default not set qos
        vcpu_qos = '-1'
        vcpu_qos = body.get('vcpu_qos')
        try:
            task = self.ics_manager.vm.set_vcpu_qos(vm_id,vcpu_qos)
            return dict({'result':'success'})
        except Exception as e:
            LOG.error('Error to set cpu qos of vm "%s", data is "%s", '
                      'error message is "%s".'
                      % (vm_id, json.dumps(body), e.message))
            return dict(result='fail', error=e.message)

class CpuQos(extensions.V21APIExtensionBase):

    name = "CpuQos"
    alias = ALIAS
    version = 1

    def get_resources(self):
        resources = [extensions.ResourceExtension(ALIAS, CpuQosController())]
        return resources

    def get_controller_extensions(self):
        return []

