import unify

# Meta Providers #
# ---------------#


def test_quality():
    for pre in ("", "highest-"):
        unify.Unify(f"claude-3-opus@{pre}quality").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}q").generate("Hello.")


def test_ttft():
    for pre in ("", "lowest-"):
        unify.Unify(f"claude-3-opus@{pre}time-to-first-token").generate("Hello.")
        unify.Unify(f"gpt-4o@{pre}ttft").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}t").generate("Hello.")


def test_itl():
    for pre in ("", "lowest-"):
        unify.Unify(f"claude-3-opus@{pre}inter-token-latency").generate("Hello.")
        unify.Unify(f"gpt-4o@{pre}itl").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}i").generate("Hello.")


def test_cost():
    for pre in ("", "lowest-"):
        unify.Unify(f"claude-3-opus@{pre}cost").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}c").generate("Hello.")


def test_input_cost():
    for pre in ("", "lowest-"):
        unify.Unify(f"claude-3-opus@{pre}input-cost").generate("Hello.")
        unify.Unify(f"gpt-4o@{pre}ic").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}i").generate("Hello.")


def test_output_cost():
    for pre in ("", "lowest-"):
        unify.Unify(f"claude-3-opus@{pre}output-cost").generate("Hello.")
        unify.Unify(f"mixtral-8x22b-instruct-v0.1@{pre}oc").generate("Hello.")


# Thresholds #
# -----------#


def test_thresholds():
    unify.Unify("llama-3.1-405b-chat@inter-token-latency|c<5").generate("Hello.")
    unify.Unify(
        "llama-3.1-70b-chat@quality|input-cost<=0.8|output-cost<=0.8|itl>1|itl<20",
    ).generate("Hello.")


# Routing #
# --------#


def test_routing():
    unify.Unify(
        "router@quality|input-cost<0.8|output-cost<0.6|itl<20",
    ).generate("Hello.")


def test_routing_w_custom_metric():
    unify.Unify("router@q:1|i:0.5|t:2|c:0.7").generate("Hello.")
    unify.Unify("router@q:1|i:0.5").generate("Hello.")


# Search Space #
# -------------#


def test_routing_w_providers():
    unify.Unify(
        "llama-3.1-405b-chat@itl|providers:groq,fireworks-ai,together-ai",
    ).generate("Hello.")


def test_routing_skip_providers():
    unify.Unify(
        "llama-3.1-405b-chat@itl|skip_providers:vertex-ai,aws-bedrock",
    ).generate("Hello.")


def test_routing_w_models():
    unify.Unify(
        "router@q:1|i:0.5|models:gpt-4o,o1-preview,claude-3-sonnet",
    ).generate("Hello.")


def test_routing_skip_models():
    unify.Unify(
        "router@q:1|i:0.5|skip_models:gpt-4o,o1-preview,claude-3-sonnet",
    ).generate("Hello.")


def test_routing_w_models_skip_providers():
    unify.Unify(
        "router@q:1|i:0.5|models:claude-3-haiku,claude-3-sonnet|"
        "skip_providers:aws-bedrock",
    ).generate("Hello.")


def test_routing_w_providers_skip_models():
    unify.Unify(
        "router@q:1|i:0.5|providers:aws-bedrock|skip_models:claude-3-haiku",
    ).generate("Hello.")


if __name__ == "__main__":
    pass
