from factum import Fact

from factum.example import dag


def main():
    extract = Fact(dag.basic_2.detail_1.extract)
    transform = Fact(dag.basic_2.detail_1.transform, inputs={'e': extract})
    load = Fact(dag.basic_2.concept_1, inputs={'t': transform})

    return load.run()

if __name__ == '__main__':
    print(main())
