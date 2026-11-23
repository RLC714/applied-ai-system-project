"""Input guardrails and logging for PawPal+."""
import logging
import re

from pawpal_system import Task

logger = logging.getLogger("pawpal")

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
VALID_FREQUENCIES = ("once", "daily", "weekly")
MAX_DESCRIPTION_LENGTH = 80


def validate_task_inputs(description, time_str, frequency):
    """Return a list of problems with the task inputs (empty list means valid)."""
    errors = []
    if not isinstance(description, str) or not description.strip():
        errors.append("Description cannot be empty.")
    elif len(description.strip()) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer.")
    if not isinstance(time_str, str) or not TIME_PATTERN.match(time_str):
        errors.append(f"Time must be HH:MM in 24-hour format, got {time_str!r}.")
    if frequency not in VALID_FREQUENCIES:
        errors.append(f"Frequency must be one of {VALID_FREQUENCIES}, got {frequency!r}.")
    return errors


def make_task(description, time_str, frequency="once"):
    """Validate inputs, then build a Task. Raises ValueError with all problems found."""
    errors = validate_task_inputs(description, time_str, frequency)
    if errors:
        logger.warning("Rejected task %r at %r: %s", description, time_str, "; ".join(errors))
        raise ValueError(" ".join(errors))
    task = Task(description.strip(), time_str, frequency)
    logger.info("Created task %r at %s (%s)", task.description, time_str, frequency)
    return task