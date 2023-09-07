from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor

def main():
    distributor: Distributor = Distributor( application_name='test')
    configuration = ConnectionConfiguration( mca='224.44.44.44', mca_port=4444, eth_device='')
    connection = distributor.create_connection( configuration )


if __name__ == '__main__':
    main()