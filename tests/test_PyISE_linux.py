from PyISE import PyISE


def test_synthesize():
    ise = PyISE(["SimpleCPU.v"], "SimpleCPU",
                ["SimpleCPU.v", "VSCPU_tb.v", "blram.v"],
                "VSCPU_tb", ["data.v"])
    ise.synthesize('.')


def test_simulation():
    ise = PyISE(["SimpleCPU.v"], "SimpleCPU",
                ["SimpleCPU.v", "VSCPU_tb.v", "blram.v"],
                "VSCPU_tb", ["data.v"])
    ise.simulate('.')


if __name__ == "__main__":
    test_synthesize()
    test_simulation()
