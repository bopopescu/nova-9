import json
import traceback
from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova.policies import ics_datastore as icsds_policies

LOG = logging.getLogger(__name__)

ALIAS = "icsdatastore"


class IcsDataStoreController(wsgi.Controller):

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(IcsDataStoreController, self).__init__()

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
        data = {'param': 'test icsdatastore'}
        return data

    @extensions.expected_errors(404)
    def show(self, req, id):
        """Return detailed information about ics datastore
        :param req: `wsgi.Request` object
        :param id: DataStore identifier
        """
        context = req.environ['nova.context']
        context.can(icsds_policies.BASE_POLICY_NAME)
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            host_datastore = self.ics_manager.host.get_storage_in_host(id)
            LOG.info('--Get datastore info from ICS-- : ' + json.dumps(host_datastore))
            return dict({'id':id, 'host_datastore':host_datastore})
        except Exception as e:
            LOG.error('Error to get datastore info from ICS : ' + traceback.format_exc())
            return dict(host_datastore=[], error=e.message)


class IcsDataStore(extensions.V21APIExtensionBase):

    name = "IcsDataStore"
    alias = ALIAS
    version = 1

    def get_resources(self):
        resources = [extensions.ResourceExtension(ALIAS, IcsDataStoreController())]
        return resources

    def get_controller_extensions(self):
        return []

