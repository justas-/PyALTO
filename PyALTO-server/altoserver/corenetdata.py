"""
PyALTO, a Python3 implementation of Application Layer Traffic Optimization protocol
Copyright (C) 2016,2017  J. Poderys, Technical University of Denmark

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Load data about network connections in CORE networks simulator
"""
import logging
import json

class CoreNetData(object):
    """Abstract details about adapter names and conenctions"""

    _bridges = {}
    _mappings = {}
    valid = False

    # _bridges = { bridge_name -> [global_a, global_b]}
    # _mappings = { hostname -> [[global, local], ...]}

    def load_data(self, filename):
        """Load data from given filename"""
        
        # Load data from the topology DB
        data = None
        with open(filename, 'r') as fp:
            data = json.loads(fp.read())

        self._bridges = data['links']
        self._mappings = data['names']

        self._validate()
        self.valid = True

    def get_nodes_global_name(self, node_name, adapter_name):
        """Given node and local adapter name, get global
        adapter name"""

        node_adapters = self._mappings.get(node_name)

        # Node not found
        if node_adapters is None:
            return None

        # Iterate over node's adapters
        for (global_name, local_name) in node_adapters:
            if local_name == adapter_name:
                return global_name
        
        # Nothing found
        return None

    def get_nodes_local_name(self, node_name, adapter_name):
        """Given node and global adapter name, get local adapter name"""

        node_adapters = self._mappings.get(node_name)

        # Node not found
        if node_adapters is None:
            return None

        # Iterate over node's adapters
        for (global_name, local_name) in node_adapters:
            if global_name == adapter_name:
                return local_name
        
        # Nothing found
        return None

    def get_adapter_names(self, src_device, dst_device):
        """Get adapter names connecting src_device with dst_device"""
        
        # Get all source device adapters
        src_node_adapters = self._mappings.get(src_device)
        if src_node_adapters is None:
            # no such device
            logging.warning('corenetdata::get_adapter_names(): Node %s has no adapters', src_device)
            return None

        # Iterate over adapters finding remote connections
        for (glob_name, loc_name) in src_node_adapters:
            remote_global = self._get_peer_adapter(glob_name)
            if remote_global is None:
                logging.warning('corenetdata::get_adapter_names(): Node %s Global %s is not connected!',
                        src_device, remote_global)
                continue

            remote_data = self._get_device_from_globname(remote_global)
            if remote_data is None:
                logging.warning('corenetdata::get_adapter_names(): Failed to get of global %s', remote_global)
                continue
            
            (remote_hostname, remote_local) = remote_data

            if remote_hostname is None:
                continue

            if remote_hostname != dst_device:
                continue

            remote_local = self.get_nodes_local_name(remote_hostname, remote_global)

            return ((glob_name, loc_name), (remote_global, remote_local))

        logging.warning('corenetdata::get_adapter_names(): Node %s has no connectiosn to %s',
                        src_device, dst_device)
        return None

    def get_remote_peer(self, src_name, src_loc_intf):
        """Given source device and local interface find
        remote device and remote local"""
        
        # Get all source device adapters
        src_node_adapters = self._mappings.get(src_name)
        if src_node_adapters is None:
            # no such device
            logging.warning('get_remote_peer(): Device %s not found', src_name)
            return None

        # Iterate over adapters finding remote connections
        for (glob_name, loc_name) in src_node_adapters:
            if loc_name != src_loc_intf:
                continue
            
            #logging.info('get_remote_peer(): node: %s local: %s global: %s',
            #        src_name, src_loc_intf, glob_name)

            remote_global = self._get_peer_adapter(glob_name)
            if remote_global is None:
                logging.warning('get_remote_peer(): Remote global not found!')
                continue

            remote_data = self._get_device_from_globname(remote_global)
            if remote_data is None:
                logging.warning('get_remote_peer(): Remote not found. Remote global: %s', remote_global)
                continue

            return remote_data

        logging.warning('get_remote_peer(): No conenction found to %s adapter %s', src_name, src_loc_intf)
        return None

    def _get_peer_adapter(self, glob_adapter):
        """Given global adapter name, find other
        end, returning global name"""

        # Iterate over all PtP conenctions
        for (peer_a, peer_b) in self._bridges.values():
            if peer_a == glob_adapter:
                return peer_b
            elif peer_b == glob_adapter:
                return peer_a

        return None

    def _get_device_from_globname(self, in_globname):
        """Get device hostname from global adapter name"""

        for hostname, adapters in self._mappings.items():
            for (glob_name, loc_name) in adapters:
                if glob_name == in_globname:
                    return (hostname, loc_name)
        return None

    def _validate(self):
        """CORE should not have any dangling (not-connected) adapters"""

        # Iterate over all bridges and ensure that we can find all hostnames
        for bridge, adapters in self._bridges.items():

            # Every bridge should have adapters            
            if not any(adapters):
                logging.error('coredata::_validate(): %s bridge has no adapters!', bridge)
                return

            (global_a, global_b) = adapters

            node_a = self._get_device_from_globname(global_a)
            node_b = self._get_device_from_globname(global_b)

            if node_a is None:
                logging.error('coredata::_validate(): No host having global adapter %s', global_a)
                return

            if node_b is None:
                logging.error('coredata::_validate(): No host having global adapter %s', global_b)
                return
