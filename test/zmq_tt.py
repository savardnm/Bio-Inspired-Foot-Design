from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def connect_to_api(port):
    client = RemoteAPIClient(port=port)
    sim = client.require('sim')
    print(f"connected to remote api on port {port}")
    return sim

def test_connection():
    # create a client to connect to zmqRemoteApi server:
    # (creation arguments can specify different host/port,
    # defaults are host='localhost', port=23000)
    client = RemoteAPIClient(port=23090)
    # get a remote object:
    print("ete sa")
    sim = client.require('sim')
    print('asf')
    # call API function:
    h = sim.getObject('/Floor')

    sim.loadScene('/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev18_Ubuntu20_04/scenes/stickbug/05-Pole-P.ttt')
    print(h)

if __name__ == '__main__':
    test_connection()
