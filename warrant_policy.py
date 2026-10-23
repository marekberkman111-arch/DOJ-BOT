"""Schvalovací pravidla SW/AW odsouhlasená vedením RP projektu."""
REQUESTER_ROLES = frozenset({"LSPD", "LSSD", "State Prosecutor"})
APPROVER_ROLES = frozenset({"Judge", "Supreme Judge", "Chief Judge"})
STATUS_DRAFT = "NAVRH"
STATUS_PENDING = "CEKA_NA_SCHVALENI"
STATUS_APPROVED = "SCHVALENO"
STATUS_REJECTED = "ZAMITNUTO"

def has_role(member, allowed):
    return bool(getattr(member.guild_permissions, "administrator", False)) or any(
        role.name in allowed for role in member.roles
    )

def can_request(member):
    return has_role(member, REQUESTER_ROLES)

def can_approve(member):
    return has_role(member, APPROVER_ROLES)

def validate_rejection(reason):
    reason = reason.strip()
    if not reason:
        raise ValueError("Při zamítnutí příkazu je povinné uvést důvod.")
    return reason
