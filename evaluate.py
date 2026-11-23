"""Evaluation harness: runs predefined PawPal+ scenarios and writes a pass/fail report."""
import os
import random
import sys
from datetime import date

from pawpal_system import Owner, Pet, Scheduler
from validation import make_task

rows = []


def check(name, expected, fn):
    """Run fn(), compare with expected, and record the result. A crash counts as a failure."""
    try:
        actual = fn()
    except Exception as exc:
        actual = f"{type(exc).__name__}: {exc}"
    passed = actual == expected
    rows.append((name, expected, actual, "Pass" if passed else "Fail"))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: expected {expected!r}, got {actual!r}")


def verdict(*args):
    """Return 'rejected' if make_task refuses these inputs, otherwise 'accepted'."""
    try:
        make_task(*args)
        return "accepted"
    except ValueError:
        return "rejected"


def new_owner():
    owner = Owner("Alex")
    buddy, mia = Pet("Buddy", "dog"), Pet("Mia", "cat")
    owner.add_pet(buddy)
    owner.add_pet(mia)
    return owner, buddy, mia


print("== Guardrails ==")
for bad_time in ("25:00", "9:5", "abc", "", "12:60"):
    check(f"time {bad_time!r} rejected", "rejected", lambda t=bad_time: verdict("Walk", t))
for desc in ("", "   ", "x" * 200):
    check(f"description {desc[:10]!r} (len {len(desc)}) rejected", "rejected",
          lambda d=desc: verdict(d, "09:00"))
check("frequency 'hourly' rejected", "rejected", lambda: verdict("Walk", "09:00", "hourly"))
for good_time in ("00:00", "09:05", "23:59"):
    check(f"time {good_time!r} accepted", "accepted", lambda t=good_time: verdict("Walk", t))

print("\n== Scheduler behavior across multiple pets ==")


def sorted_ok():
    random.seed(7)  # fixed seed so the run is reproducible
    owner, buddy, mia = new_owner()
    for i in range(40):
        t = f"{random.randint(0, 23):02d}:{random.choice(['00', '15', '30', '45'])}"
        random.choice([buddy, mia]).add_task(make_task(f"task{i}", t))
    s = Scheduler(owner)
    times = [t.time for t in s.sort_by_time(s.filter_tasks())]
    return len(times) == 40 and times == sorted(times)


check("40 random tasks across 2 pets sort chronologically", True, sorted_ok)


def conflict_count():
    owner, buddy, mia = new_owner()
    buddy.add_task(make_task("Feed", "08:00"))
    mia.add_task(make_task("Meds", "08:00"))
    mia.add_task(make_task("Play", "09:00"))
    return len(Scheduler(owner).detect_conflicts())


check("one cross-pet conflict detected", 1, conflict_count)


def conflict_clears_when_done():
    owner, buddy, mia = new_owner()
    t1, t2 = make_task("Feed", "08:00"), make_task("Meds", "08:00")
    buddy.add_task(t1)
    mia.add_task(t2)
    s = Scheduler(owner)
    s.mark_task_complete(t1)
    return len(s.detect_conflicts())


check("completed task no longer conflicts", 0, conflict_clears_when_done)


def recurrence_gap(freq):
    owner, buddy, _ = new_owner()
    task = make_task("Repeat", "08:00", freq)
    buddy.add_task(task)
    nxt = Scheduler(owner).mark_task_complete(task)
    return (nxt.due_date - task.due_date).days


check("daily task recurs 1 day later", 1, lambda: recurrence_gap("daily"))
check("weekly task recurs 7 days later", 7, lambda: recurrence_gap("weekly"))


def once_does_not_recur():
    owner, buddy, _ = new_owner()
    task = make_task("Bath", "10:00", "once")
    buddy.add_task(task)
    return Scheduler(owner).mark_task_complete(task)


check("one-time task does not recur", None, once_does_not_recur)


def filter_by_pet():
    owner, buddy, mia = new_owner()
    buddy.add_task(make_task("Feed", "08:00"))
    mia.add_task(make_task("Meds", "09:00"))
    return len(Scheduler(owner).filter_tasks(pet_name="Mia"))


check("filter by pet returns only that pet's tasks", 1, filter_by_pet)


def empty_safe():
    owner, _, _ = new_owner()
    s = Scheduler(owner)
    return (s.sort_by_time(s.filter_tasks()), s.detect_conflicts())


check("pets with no tasks handled safely", ([], []), empty_safe)

passed = sum(1 for r in rows if r[3] == "Pass")
os.makedirs("logs", exist_ok=True)
with open("logs/evaluation_report.md", "w", encoding="utf-8") as f:
    f.write(f"# Evaluation report ({date.today()})\n\n")
    f.write("| Test | Expected | Actual | Result |\n|---|---|---|---|\n")
    for name, exp, act, res in rows:
        f.write(f"| {name} | `{exp}` | `{act}` | {res} |\n")
    f.write(f"\n**Summary: {passed}/{len(rows)} checks passed**\n")

print(f"\nSummary: {passed}/{len(rows)} checks passed")
sys.exit(0 if passed == len(rows) else 1)