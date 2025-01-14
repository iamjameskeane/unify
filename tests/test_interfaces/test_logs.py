import math
import asyncio
import pytest
import threading

import unify
from .helpers import _handle_project


# Functional Compositions #
# ------------------------#


def test_get_log_by_value_no_project():
    if "_" in unify.list_projects():
        unify.delete_project("_")
    data = {
        "system_prompt": "You are a weather assistant",
        "user_prompt": "hello world",
    }
    assert len(unify.get_logs()) == 0
    log = unify.log(**data)
    retrieved_log = unify.get_log_by_value(**data)
    assert log == retrieved_log
    log.delete()
    assert unify.get_log_by_value(**data) is None
    unify.delete_project("_")


@_handle_project
def test_get_log_by_value():
    data = {
        "system_prompt": "You are a weather assistant",
        "user_prompt": "hello world",
    }
    assert len(unify.get_logs()) == 0
    log = unify.log(**data)
    retrieved_log = unify.get_log_by_value(**data)
    assert log == retrieved_log
    log.delete()
    assert unify.get_log_by_value(**data) is None


@_handle_project
def test_get_logs_by_value():
    data = {
        "system_prompt": "You are a weather assistant",
        "user_prompt": "hello world",
    }
    assert len(unify.get_logs()) == 0
    log0 = unify.log(**data, skip_duplicates=False)
    log1 = unify.log(**data, skip_duplicates=False)
    retrieved_logs = unify.get_logs_by_value(**data)
    assert len(retrieved_logs) == 2
    for log, retrieved_log in zip((log0, log1), retrieved_logs):
        assert log == retrieved_log
    log0.delete()
    retrieved_logs = unify.get_logs_by_value(**data)
    assert len(retrieved_logs) == 1
    assert log1 == retrieved_logs[0]
    log1.delete()
    assert unify.get_logs_by_value(**data) == []


@_handle_project
def test_replace_log_entries():
    data = {
        "system_prompt": "You are a weather assistant",
        "user_prompt": "hello world",
    }
    assert len(unify.get_logs()) == 0
    log = unify.log(**data)
    assert unify.get_log_by_id(log.id).entries == data
    assert len(unify.get_logs()) == 1
    new_data = {
        "system_prompt": "You are a maths assistant",
        "user_prompt": "hi earth",
    }
    log.replace_entries(**new_data)
    assert log.entries == new_data
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries == new_data


@_handle_project
def test_update_log_entries():
    messages = [
        {
            "role": "assistant",
            "context": "you are a helpful assistant",
        },
    ]
    assert len(unify.get_logs()) == 0
    log = unify.log(messages=messages)
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries["messages"] == messages
    new_messages = [
        {
            "role": "user",
            "context": "what is 1 + 1?",
        },
    ]
    log.update_entries(lambda x, y: x + y, messages=new_messages)
    combined_messages = messages + new_messages
    assert log.entries["messages"] == combined_messages
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries["messages"] == combined_messages


@_handle_project
def test_update_log_entries_w_dict():
    messages = [
        {
            "role": "assistant",
            "context": "you are a helpful assistant",
        },
    ]
    name = "John"
    assert len(unify.get_logs()) == 0
    log = unify.log(messages=messages, name=name)
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries["messages"] == messages
    new_messages = [
        {
            "role": "user",
            "context": "what is 1 + 1?",
        },
    ]
    surname = "Smith"
    log.update_entries(
        {
            "messages": lambda x, y: x + y,
            "name": lambda x, y: f"{x} {y}",
        },
        messages=new_messages,
        name=surname,
    )
    combined_messages = messages + new_messages
    assert log.entries["messages"] == combined_messages
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries["messages"] == combined_messages


@_handle_project
def test_rename_log_entries():
    customer = "John Smith"
    assert len(unify.get_logs()) == 0
    log = unify.log(customer=customer)
    assert len(unify.get_logs()) == 1
    assert unify.get_log_by_id(log.id).entries["customer"] == customer
    log.rename_entries(customer="customer_name")
    assert "customer" not in log.entries
    assert "customer_name" in log.entries
    assert len(unify.get_logs()) == 1
    retrieved_log = unify.get_log_by_id(log.id)
    assert "customer" not in retrieved_log.entries
    assert "customer_name" in retrieved_log.entries


@_handle_project
def test_get_logs_with_fields():
    assert len(unify.get_logs()) == 0
    unify.log(customer="John Smith")
    assert len(unify.get_logs_with_fields("customer")) == 1
    assert len(unify.get_logs_with_fields("dummy")) == 0
    unify.log(seller="Maggie Jones")
    assert (
        len(
            unify.get_logs_with_fields(
                "customer",
                "seller",
                mode="all",
            ),
        )
        == 0
    )
    assert (
        len(
            unify.get_logs_with_fields(
                "customer",
                "seller",
                mode="any",
            ),
        )
        == 2
    )


@_handle_project
def test_get_logs_without_fields():
    assert len(unify.get_logs()) == 0
    unify.log(customer="John Smith")
    assert len(unify.get_logs_without_fields("customer")) == 0
    assert len(unify.get_logs_without_fields("dummy")) == 1
    unify.log(seller="Maggie Jones")
    assert (
        len(
            unify.get_logs_without_fields(
                "customer",
                "seller",
                mode="all",
            ),
        )
        == 2
    )
    assert (
        len(
            unify.get_logs_without_fields(
                "customer",
                "seller",
                mode="any",
            ),
        )
        == 0
    )


@_handle_project
def test_group_logs_by_params():
    logs = list()
    log_idx = 0
    qs = ["1+1", "2+2", "3+3", "4+1"]
    for system_prompt in ["You are an expert.", "You are an expert mathematician."]:
        for dataset_version in ["vanilla", "with_failures", "with_successes"]:
            params = dict(
                system_prompt=system_prompt,
                dataset_version=dataset_version,
            )
            for q in qs:
                logs.append(unify.Log(id=log_idx, q=q, params=params))
                log_idx += 1
    grouped_logs = unify.group_logs_by_configs(logs=logs)
    assert len(grouped_logs) == 6
    assert list(grouped_logs.keys()) == [
        '{"system_prompt": "You are an expert.", ' '"dataset_version": "vanilla"}',
        '{"system_prompt": "You are an expert.", '
        '"dataset_version": "with_failures"}',
        '{"system_prompt": "You are an expert.", '
        '"dataset_version": "with_successes"}',
        '{"system_prompt": "You are an expert mathematician.", '
        '"dataset_version": "vanilla"}',
        '{"system_prompt": "You are an expert mathematician.", '
        '"dataset_version": "with_failures"}',
        '{"system_prompt": "You are an expert mathematician.", '
        '"dataset_version": "with_successes"}',
    ]


# Context Handlers #
# -----------------#

# Log


@_handle_project
def test_with_log():

    with unify.Log(a="a"):
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a"}
        unify.add_log_entries(b="b", c="c")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a", "b": "b", "c": "c"}
        with unify.Log(d="d"):
            logs = unify.get_logs()
            assert len(logs) == 2
            assert logs[1].entries == {"d": "d"}
            unify.add_log_entries(e="e", f="f")
            logs = unify.get_logs()
            assert len(logs) == 2
            assert logs[1].entries == {"d": "d", "e": "e", "f": "f"}
        unify.add_log_entries(g="g")
        logs = unify.get_logs()
        assert len(logs) == 2
        assert logs[0].entries == {"a": "a", "b": "b", "c": "c", "g": "g"}


@_handle_project
def test_global_logging():

    with unify.Log(a="a"):
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a"}
        unify.log(b="b", c="c")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a", "b": "b", "c": "c"}
        with unify.Log(d="d"):
            logs = unify.get_logs()
            assert len(logs) == 2
            assert logs[1].entries == {"d": "d"}
            unify.log(e="e", f="f")
            logs = unify.get_logs()
            assert len(logs) == 2
            assert logs[1].entries == {"d": "d", "e": "e", "f": "f"}
        unify.log(g="g")
        logs = unify.get_logs()
        assert len(logs) == 2
        assert logs[0].entries == {"a": "a", "b": "b", "c": "c", "g": "g"}


@_handle_project
def test_with_log_threaded():

    def fn(a, b, c, d, e, f, g):
        with unify.Log(a=a):
            unify.add_log_entries(b=b, c=c)
            with unify.Log(d=d):
                unify.add_log_entries(e=e, f=f)
            unify.add_log_entries(g=g)

    threads = [
        threading.Thread(
            target=fn,
            args=[7 * i + j for j in range(7)],
        )
        for i in range(4)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]

    logs = unify.get_logs()
    entries = [log.entries for log in logs]

    assert sorted([sorted(d.items()) for d in entries]) == [
        [("a", i * 7), ("b", i * 7 + 1), ("c", i * 7 + 2), ("g", i * 7 + 6)]
        for i in range(4)
    ] + [[("d", i * 7 + 3), ("e", i * 7 + 4), ("f", i * 7 + 5)] for i in range(4)]


@_handle_project
@pytest.mark.asyncio
async def test_with_log_async():

    async def fn(a, b, c, d, e, f, g):
        with unify.Log(a=a):
            unify.add_log_entries(b=b, c=c)
            with unify.Log(d=d):
                unify.add_log_entries(e=e, f=f)
            unify.add_log_entries(g=g)

    fns = [fn(*[7 * i + j for j in range(7)]) for i in range(4)]
    await asyncio.gather(*fns)

    logs = unify.get_logs()
    entries = [log.entries for log in logs]

    assert sorted([sorted(d.items()) for d in entries]) == [
        [("a", i * 7), ("b", i * 7 + 1), ("c", i * 7 + 2), ("g", i * 7 + 6)]
        for i in range(4)
    ] + [[("d", i * 7 + 3), ("e", i * 7 + 4), ("f", i * 7 + 5)] for i in range(4)]


# Context


@_handle_project
def test_with_context():

    unify.log(a="a")
    logs = unify.get_logs()
    assert len(logs) == 1
    assert logs[0].entries == {"a": "a"}
    with unify.Context("capitalized"):
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a"}
        unify.add_log_entries(logs=logs, b="B")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a", "capitalized/b": "B"}
        with unify.Context("vowels"):
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {"a": "a", "capitalized/b": "B"}
            unify.add_log_entries(logs=logs, e="E")
            unify.add_log_params(logs=logs, u="U")
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {
                "a": "a",
                "capitalized/b": "B",
                "capitalized/vowels/e": "E",
            }
            assert logs[0].params == {
                "capitalized/vowels/u": "U",
            }
            unify.log(a="A")
    logs = unify.get_logs()
    assert len(logs) == 2
    assert logs[0].entries == {
        "a": "a",
        "capitalized/b": "B",
        "capitalized/vowels/e": "E",
    }
    assert logs[1].entries == {
        "capitalized/vowels/a": "A",
    }


@_handle_project
def test_with_context_default_project():
    with unify.Log():
        with unify.Context("science"):
            with unify.Context("physics"):
                unify.log(score=1.0)
            with unify.Context("chemistry"):
                unify.log(score=0.5)
            with unify.Context("biology"):
                unify.log(score=0.0)

    entries = unify.get_logs()[0].entries
    assert entries["science/physics/score"] == 1.0
    assert entries["science/chemistry/score"] == 0.5
    assert entries["science/biology/score"] == 0.0


@_handle_project
def test_with_context_threaded():

    def fn(a, b, e):
        log = unify.log(a=a)
        with unify.Context("capitalized"):
            log.add_entries(b=b)
            with unify.Context("vowels"):
                log.add_entries(e=e)
                unify.log(a=a)

    threads = [
        threading.Thread(
            target=fn,
            args=[3 * i + j for j in range(3)],
        )
        for i in range(4)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]

    logs = unify.get_logs()
    entries = sorted(
        [log.entries for log in logs],
        key=lambda dct: list(dct.values())[0],
    )
    for i, entry in enumerate(entries[0::2]):
        assert entry == {
            "a": i * 3,
            "capitalized/b": i * 3 + 1,
            "capitalized/vowels/e": i * 3 + 2,
        }
    for i, entry in enumerate(entries[1::2]):
        assert entry == {"capitalized/vowels/a": i * 3}


@_handle_project
@pytest.mark.asyncio
async def test_with_context_async():

    async def fn(a, b, e):
        log = unify.log(a=a)
        with unify.Context("capitalized"):
            log.add_entries(b=b)
            with unify.Context("vowels"):
                log.add_entries(e=e)
                unify.log(a=a)

    fns = [fn(*[3 * i + j for j in range(3)]) for i in range(4)]
    await asyncio.gather(*fns)

    logs = unify.get_logs()
    entries = sorted(
        [log.entries for log in logs],
        key=lambda dct: list(dct.values())[0],
    )
    for i, entry in enumerate(entries[0::2]):
        assert entry == {
            "a": i * 3,
            "capitalized/b": i * 3 + 1,
            "capitalized/vowels/e": i * 3 + 2,
        }
    for i, entry in enumerate(entries[1::2]):
        assert entry == {"capitalized/vowels/a": i * 3}


# Entries


@_handle_project
def test_with_entries():

    with unify.Entries(a="a"):
        logs = unify.get_logs()
        assert len(logs) == 0
        log = unify.log()
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a"}
        unify.add_log_entries(logs=log, b="b", c="c")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {"a": "a", "b": "b", "c": "c"}
        with unify.Entries(d="d"):
            unify.add_log_entries(logs=log)
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {"a": "a", "b": "b", "c": "c", "d": "d"}
            unify.add_log_entries(logs=log, e="e", f="f")
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {
                "a": "a",
                "b": "b",
                "c": "c",
                "d": "d",
                "e": "e",
                "f": "f",
            }
        unify.add_log_entries(logs=log, g="g")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].entries == {
            "a": "a",
            "b": "b",
            "c": "c",
            "d": "d",
            "e": "e",
            "f": "f",
            "g": "g",
        }


@_handle_project
def test_with_entries_threaded():

    def fn(a, b, c, d, e, f, g):
        with unify.Entries(a=a):
            log = unify.log()
            unify.add_log_entries(logs=log, b=b, c=c)
            with unify.Entries(d=d):
                unify.add_log_entries(logs=log)
                unify.add_log_entries(logs=log, e=e, f=f)
            unify.add_log_entries(logs=log, g=g)

    threads = [
        threading.Thread(
            target=fn,
            args=[7 * i + j for j in range(7)],
        )
        for i in range(4)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]

    logs = unify.get_logs()
    entries = [log.entries for log in logs]

    assert sorted([sorted(d.items()) for d in entries]) == [
        [
            ("a", i * 7),
            ("b", i * 7 + 1),
            ("c", i * 7 + 2),
            ("d", i * 7 + 3),
            ("e", i * 7 + 4),
            ("f", i * 7 + 5),
            ("g", i * 7 + 6),
        ]
        for i in range(4)
    ]


@_handle_project
@pytest.mark.asyncio
async def test_with_entries_async():

    async def fn(a, b, c, d, e, f, g):
        with unify.Entries(a=a):
            log = unify.log()
            unify.add_log_entries(logs=log, b=b, c=c)
            with unify.Entries(d=d):
                unify.add_log_entries(logs=log)
                unify.add_log_entries(logs=log, e=e, f=f)
            unify.add_log_entries(logs=log, g=g)

    fns = [fn(*[7 * i + j for j in range(7)]) for i in range(4)]
    await asyncio.gather(*fns)

    logs = unify.get_logs()
    entries = [log.entries for log in logs]

    assert sorted([sorted(d.items()) for d in entries]) == [
        [
            ("a", i * 7),
            ("b", i * 7 + 1),
            ("c", i * 7 + 2),
            ("d", i * 7 + 3),
            ("e", i * 7 + 4),
            ("f", i * 7 + 5),
            ("g", i * 7 + 6),
        ]
        for i in range(4)
    ]


# Params


@_handle_project
def test_with_params():

    with unify.Params(a="a"):
        logs = unify.get_logs()
        assert len(logs) == 0
        log = unify.log()
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].params == {"a": "a"}
        unify.add_log_params(logs=log, b="b", c="c")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].params == {"a": "a", "b": "b", "c": "c"}
        with unify.Params(d="d"):
            unify.add_log_params(logs=log)
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].params == {"a": "a", "b": "b", "c": "c", "d": "d"}
            unify.add_log_params(logs=log, e="e", f="f")
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].params == {
                "a": "a",
                "b": "b",
                "c": "c",
                "d": "d",
                "e": "e",
                "f": "f",
            }
        unify.add_log_params(logs=log, g="g")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].params == {
            "a": "a",
            "b": "b",
            "c": "c",
            "d": "d",
            "e": "e",
            "f": "f",
            "g": "g",
        }


@_handle_project
def test_with_params_threaded():

    def fn(a, b, c, d, e, f, g):
        with unify.Params(a=a):
            log = unify.log()
            unify.add_log_params(logs=log, b=b, c=c)
            with unify.Params(d=d):
                unify.add_log_params(logs=log)
                unify.add_log_params(logs=log, e=e, f=f)
            unify.add_log_params(logs=log, g=g)

    threads = [
        threading.Thread(
            target=fn,
            args=[7 * i + j for j in range(7)],
        )
        for i in range(4)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]

    logs = unify.get_logs()
    params = [log.params for log in logs]

    assert sorted([sorted(d.items()) for d in params]) == [
        [
            ("a", i * 7),
            ("b", i * 7 + 1),
            ("c", i * 7 + 2),
            ("d", i * 7 + 3),
            ("e", i * 7 + 4),
            ("f", i * 7 + 5),
            ("g", i * 7 + 6),
        ]
        for i in range(4)
    ]


@_handle_project
@pytest.mark.asyncio
async def test_with_params_async():

    async def fn(a, b, c, d, e, f, g):
        with unify.Params(a=a):
            log = unify.log()
            unify.add_log_params(logs=log, b=b, c=c)
            with unify.Params(d=d):
                unify.add_log_params(logs=log)
                unify.add_log_params(logs=log, e=e, f=f)
            unify.add_log_params(logs=log, g=g)

    fns = [fn(*[7 * i + j for j in range(7)]) for i in range(4)]
    await asyncio.gather(*fns)

    logs = unify.get_logs()
    params = [log.params for log in logs]

    assert sorted([sorted(d.items()) for d in params]) == [
        [
            ("a", i * 7),
            ("b", i * 7 + 1),
            ("c", i * 7 + 2),
            ("d", i * 7 + 3),
            ("e", i * 7 + 4),
            ("f", i * 7 + 5),
            ("g", i * 7 + 6),
        ]
        for i in range(4)
    ]


# Combos


@_handle_project
def test_with_all():

    with unify.Params(a="a"):
        logs = unify.get_logs()
        assert len(logs) == 0
        log = unify.log()
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].params == {"a": "a"}
        unify.add_log_params(logs=log, b="b", c="c")
        logs = unify.get_logs()
        assert len(logs) == 1
        assert logs[0].params == {"a": "a", "b": "b", "c": "c"}
        with unify.Entries(d="d"):
            unify.add_log_entries(logs=log)
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {"d": "d"}
            assert logs[0].params == {"a": "a", "b": "b", "c": "c"}
            unify.add_log_entries(logs=log, e="e")
            unify.add_log_params(logs=log, f="f")
            logs = unify.get_logs()
            assert len(logs) == 1
            assert logs[0].entries == {"d": "d", "e": "e"}
            assert logs[0].params == {
                "a": "a",
                "b": "b",
                "c": "c",
                "f": "f",
            }
            with unify.Log():
                unify.add_log_params(g="g")
                unify.add_log_entries(h="h")
                logs = unify.get_logs()
                assert len(logs) == 2
                assert logs[1].params == {"a": "a", "g": "g"}
                assert logs[1].entries == {"d": "d", "h": "h"}
            unify.add_log_entries(logs=log, i="i")
            logs = unify.get_logs()
            assert len(logs) == 2
            assert logs[0].entries == {"d": "d", "e": "e", "i": "i"}
            assert logs[0].params == {
                "a": "a",
                "b": "b",
                "c": "c",
                "f": "f",
            }


@_handle_project
def test_with_all_threaded():
    def fn(a, b, c, d, e, f, g, h, i):
        with unify.Params(a=a):
            log = unify.log()
            unify.add_log_params(logs=log, b=b, c=c)
            with unify.Entries(d=d):
                unify.add_log_entries(logs=log)
                unify.add_log_entries(logs=log, e=e)
                unify.add_log_params(logs=log, f=f)
                with unify.Log():
                    unify.add_log_params(g=g)
                    unify.add_log_entries(h=h)
                unify.add_log_entries(logs=log, i=i)

    threads = [
        threading.Thread(
            target=fn,
            args=[9 * i + j for j in range(9)],
        )
        for i in range(4)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]

    logs = unify.get_logs()

    params = [log.params for log in logs]
    observed = [sorted(d.items()) for d in sorted(params, key=lambda x: x["a"])]
    for i, obs in enumerate(observed):
        if i % 2 == 0:
            assert obs == [
                ("a", (i / 2) * 9),
                ("b", (i / 2) * 9 + 1),
                ("c", (i / 2) * 9 + 2),
                ("f", (i / 2) * 9 + 5),
            ]
        else:
            assert obs == [
                ("a", math.floor(i / 2) * 9),
                ("g", math.floor(i / 2) * 9 + 6),
            ]
    entries = [log.entries for log in logs]
    observed = [sorted(d.items()) for d in sorted(entries, key=lambda x: x["d"])]
    for i, obs in enumerate(observed):
        if i % 2 == 0:
            assert obs == [
                ("d", (i / 2) * 9 + 3),
                ("e", (i / 2) * 9 + 4),
                ("i", (i / 2) * 9 + 8),
            ]
        else:
            assert obs == [
                ("d", math.floor(i / 2) * 9 + 3),
                ("h", math.floor(i / 2) * 9 + 7),
            ]


@_handle_project
@pytest.mark.asyncio
async def test_with_all_async():

    async def fn(a, b, c, d, e, f, g, h, i):
        with unify.Params(a=a):
            log = unify.log()
            unify.add_log_params(logs=log, b=b, c=c)
            with unify.Entries(d=d):
                unify.add_log_entries(logs=log)
                unify.add_log_entries(logs=log, e=e)
                unify.add_log_params(logs=log, f=f)
                with unify.Log():
                    unify.add_log_params(g=g)
                    unify.add_log_entries(h=h)
                unify.add_log_entries(logs=log, i=i)

    fns = [fn(*[9 * i + j for j in range(9)]) for i in range(4)]
    await asyncio.gather(*fns)

    logs = unify.get_logs()

    params = [log.params for log in logs]
    observed = [sorted(d.items()) for d in sorted(params, key=lambda x: x["a"])]
    for i, obs in enumerate(observed):
        if i % 2 == 0:
            assert obs == [
                ("a", (i / 2) * 9),
                ("b", (i / 2) * 9 + 1),
                ("c", (i / 2) * 9 + 2),
                ("f", (i / 2) * 9 + 5),
            ]
        else:
            assert obs == [
                ("a", math.floor(i / 2) * 9),
                ("g", math.floor(i / 2) * 9 + 6),
            ]
    entries = [log.entries for log in logs]
    observed = [sorted(d.items()) for d in sorted(entries, key=lambda x: x["d"])]
    for i, obs in enumerate(observed):
        if i % 2 == 0:
            assert obs == [
                ("d", (i / 2) * 9 + 3),
                ("e", (i / 2) * 9 + 4),
                ("i", (i / 2) * 9 + 8),
            ]
        else:
            assert obs == [
                ("d", math.floor(i / 2) * 9 + 3),
                ("h", math.floor(i / 2) * 9 + 7),
            ]


if __name__ == "__main__":
    pass
