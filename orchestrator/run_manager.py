import uuid
from memory.run_store import create_run, append_event, complete_run
from orchestrator.event_models import AgentEvent
from orchestrator.planner import plan_stream
from orchestrator.executor import execute_stream

async def stream_run(goal: str, model: str = "gpt-4o-mini"):
    run_id = str(uuid.uuid4())
    create_run(run_id, goal)

    # Planner
    ev = AgentEvent(type="planner_started", run_id=run_id, agent="planner", status="thinking")
    append_event(run_id, ev.model_dump())
    yield ev.to_sse()

    plan_text = ""
    async for delta in plan_stream(goal, model):
        plan_text += delta
        ev = AgentEvent(type="planner_chunk", run_id=run_id, agent="planner",
                        status="streaming", content=delta)
        yield ev.to_sse()

    steps = [l.strip() for l in plan_text.strip().splitlines() if l.strip()]
    ev = AgentEvent(type="planner_completed", run_id=run_id, agent="planner",
                    status="done", content={"steps": steps})
    append_event(run_id, ev.model_dump())
    yield ev.to_sse()

    # Executor
    for step in steps:
        ev = AgentEvent(type="tool_started", run_id=run_id, agent="executor",
                        step=step, status="thinking")
        append_event(run_id, ev.model_dump())
        yield ev.to_sse()

        async for delta in execute_stream(step, model):
            ev = AgentEvent(type="tool_chunk", run_id=run_id, agent="executor",
                            step=step, status="streaming", content=delta)
            yield ev.to_sse()

        ev = AgentEvent(type="tool_completed", run_id=run_id, agent="executor",
                        step=step, status="done")
        append_event(run_id, ev.model_dump())
        yield ev.to_sse()

    ev = AgentEvent(type="run_completed", run_id=run_id, status="done")
    complete_run(run_id, {"steps": steps})
    yield ev.to_sse()
