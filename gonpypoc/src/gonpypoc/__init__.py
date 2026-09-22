from gonpypoc.cgotopypoc import assert_returns


def main() -> None:
    results = assert_returns()
    print("cgotopypoc: all compatible Python return types validated")
    for name, value, py_type in results:
        print(f"  {name}: {value!r} ({py_type.__name__})")
