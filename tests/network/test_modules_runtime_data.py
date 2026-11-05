from ocrd_network.runtime_data.hosts import DataHost


def test_worker_instances_are_independent():
    host = DataHost(
        host="localhost",
        username="user",
        password="password",
        keypath="",
        workers=[
            {
                "name": "ocrd-example",
                "number_of_instance": 3,
                "deploy_type": "native"
            }
        ],
        servers=[]
    )

    workers = host.workers_native

    assert len(workers) == 3
    assert workers[0] is not workers[1]
    assert workers[1] is not workers[2]
    assert workers[0] is not workers[2]

    workers[0].pid = "123"

    assert workers[0].pid == "123"
    assert workers[1].pid is None
    assert workers[2].pid is None
