"""Build and audit the diverse Gate 3G-R promotion benchmark before execution."""
from __future__ import annotations

import hashlib, json, re
from itertools import combinations
from collections import Counter
from pathlib import Path


def item(i, text, role, family, field=None, operator=None, value=None, spans=None):
    s = {"text": text, "role": role}
    if field: s.update({"field": field, "operator": operator, "value": value})
    return {"id": f"g3gr-{i:03d}", "request": text, "pattern_family": family, "spans": spans or [s]}


def build():
    required = [
        ("I need candidates who can work in London", "required-eligibility", "location", "eq", "london"),
        ("London-based applicants are a non-negotiable requirement", "required-non-negotiable", "location", "eq", "london"),
        ("The role is eligible only for senior search engineers", "required-only", "seniority", "gte", "senior"),
        ("Please treat Healthcare expertise as mandatory", "required-mandatory", "industry", "eq", "healthcare"),
        ("A minimum of 15 years of experience is needed", "required-threshold", "years_experience", "gte", 15),
        ("Applicants must demonstrate over 12 years in the field", "required-threshold", "years_experience", "gt", 12),
        ("Exactly 8 years is the eligibility threshold", "required-threshold", "years_experience", "eq", 8),
        ("Only principal-level candidates should be returned", "required-only", "seniority", "gte", "principal"),
        ("Eligibility depends on being based in Lisbon", "required-eligibility", "location", "eq", "lisbon"),
        ("We require an Energy specialist for this search", "required-explicit", "industry", "eq", "energy"),
        ("Do not include anyone below 10 years of experience", "required-negated-minimum", "years_experience", "gte", 10),
        ("Candidates need at least 20 years to qualify", "required-threshold", "years_experience", "gte", 20),
        ("The shortlist must contain Manufacturing experts", "required-explicit", "industry", "eq", "manufacturing"),
        ("A seniority of senior or higher is required", "required-explicit", "seniority", "gte", "senior"),
        ("This request is restricted to Berlin locations", "required-restriction", "location", "eq", "berlin"),
        ("Non-negotiably, applicants need Retail experience", "required-non-negotiable", "industry", "eq", "retail"),
        ("The minimum acceptable experience is 5 years", "required-threshold", "years_experience", "gte", 5),
        ("Please return Technology specialists, and no others", "required-only", "industry", "eq", "technology"),
        ("To qualify, a person must have more than 18 years", "required-threshold", "years_experience", "gt", 18),
        ("A Paris base is essential for this assignment", "required-eligibility", "location", "eq", "paris"),
        ("The requirement is a Principal engineer", "required-explicit", "seniority", "gte", "principal"),
        ("Healthcare is an eligibility condition, not background context", "required-eligibility", "industry", "eq", "healthcare"),
        ("Applicants need no fewer than 7 years", "required-threshold", "years_experience", "gte", 7),
        ("Only Energy candidates satisfy this brief", "required-only", "industry", "eq", "energy"),
        ("A Dublin location is required for eligibility", "required-explicit", "location", "eq", "dublin"),
    ]
    excluded = [
        ("Please leave out Financial Services profiles", "excluded-explicit", "industry", "neq", "financial services"),
        ("Retail backgrounds are not eligible here", "excluded-negation", "industry", "neq", "retail"),
        ("Do not return anyone based in Madrid", "excluded-negation", "location", "neq", "madrid"),
        ("The shortlist must not contain junior candidates", "excluded-negation", "seniority", "neq", "junior"),
        ("Exclude Energy from the result set", "excluded-explicit", "industry", "neq", "energy"),
        ("No London-based profiles should appear", "excluded-negation", "location", "neq", "london"),
        ("Avoid candidates with fewer than 10 years", "excluded-negation", "years_experience", "gte", 10),
        ("Financial Services is explicitly out of scope", "excluded-explicit", "industry", "neq", "financial services"),
        ("We cannot accept a principal-level profile", "excluded-negation", "seniority", "neq", "principal"),
        ("Manufacturing should be excluded from this search", "excluded-explicit", "industry", "neq", "manufacturing"),
        ("Profiles in Berlin are prohibited", "excluded-negation", "location", "neq", "berlin"),
        ("Keep Healthcare out of the candidate pool", "excluded-explicit", "industry", "neq", "healthcare"),
        ("The request rules out senior applicants", "excluded-negation", "seniority", "neq", "senior"),
        ("Do not include under-five-year profiles", "excluded-negation", "years_experience", "gte", 5),
        ("Paris is not an acceptable base", "excluded-negation", "location", "neq", "paris"),
        ("Avoid Technology specialists for this brief", "excluded-explicit", "industry", "neq", "technology"),
        ("No Energy advisers should be suggested", "excluded-negation", "industry", "neq", "energy"),
        ("Applicants from Dublin are disallowed", "excluded-negation", "location", "neq", "dublin"),
        ("The result must contain nobody below senior", "excluded-negation", "seniority", "gte", "senior"),
        ("We specifically exclude Retail experience", "excluded-explicit", "industry", "neq", "retail"),
        ("Never return anyone with fewer than 15 years", "excluded-negation", "years_experience", "gte", 15),
        ("London is a prohibited location", "excluded-negation", "location", "neq", "london"),
        ("Do not surface Manufacturing consultants", "excluded-negation", "industry", "neq", "manufacturing"),
        ("Junior is outside the requested seniority range", "excluded-negation", "seniority", "neq", "junior"),
        ("Financial Services must be omitted", "excluded-explicit", "industry", "neq", "financial services"),
    ]
    preferred = [
        ("Senior would be a welcome qualification", "preferred-hedged"), ("A London base would be helpful", "preferred-indirect"),
        ("Healthcare experience is a nice-to-have", "preferred-nice-to-have"), ("It would be good to see Energy exposure", "preferred-indirect"),
        ("We would like, but do not require, principal profiles", "preferred-contrast"), ("A Retail background is desirable", "preferred-hedged"),
        ("Candidates with Lisbon experience are a plus", "preferred-nice-to-have"), ("Ideally the person is senior", "preferred-explicit"),
        ("The brief has a strong preference for Technology", "preferred-strong"), ("An experienced Manufacturing background would be useful", "preferred-indirect"),
        ("Preference goes to Paris-based people", "preferred-explicit"), ("Senior would be nice, though not essential", "preferred-contrast"),
        ("A Healthcare focus would strengthen the application", "preferred-indirect"), ("Bonus points for Berlin experience", "preferred-nice-to-have"),
        ("We lean toward Energy specialists", "preferred-indirect"), ("A Dublin base is favored", "preferred-hedged"),
        ("More than 10 years would be advantageous", "preferred-indirect"), ("Principal is preferred rather than mandatory", "preferred-contrast"),
        ("Financial Services familiarity is welcome", "preferred-indirect"), ("Ideally, include Retail practitioners", "preferred-explicit"),
        ("It would be a plus to have London context", "preferred-nice-to-have"), ("A senior profile is desirable", "preferred-hedged"),
        ("We would appreciate Technology experience", "preferred-indirect"), ("Energy would be a useful domain", "preferred-indirect"),
        ("A Paris location is preferred, not required", "preferred-contrast"),
    ]
    context = [
        ("People who worked on Healthcare products are relevant context", "context-project-domain"), ("The team has collaborated with London delivery groups", "context-location"),
        ("Senior stakeholders shaped the programme", "context-seniority"), ("The expert built systems for banks", "context-domain"),
        ("Their projects included Retail clients", "context-project-domain"), ("They delivered Energy analytics in practice", "context-project-domain"),
        ("A background involving Manufacturing teams is informative", "context-project-domain"), ("The profile mentions Berlin partnerships", "context-location"),
        ("Healthcare appears in the project history", "context-domain"), ("They worked alongside principal engineers", "context-seniority"),
        ("The candidate supported Technology programmes", "context-project-domain"), ("Experience spans Financial Services projects", "context-project-domain"),
        ("Their London teams were distributed", "context-location"), ("The biography describes a senior stakeholder role", "context-seniority"),
        ("They built an Energy forecasting platform", "context-project-domain"), ("The profile covers Paris delivery work", "context-location"),
        ("Retail appears in the candidate's case studies", "context-domain"), ("They partnered with Manufacturing groups", "context-project-domain"),
        ("The person has worked with Healthcare teams", "context-domain"), ("Senior reviewers approved the design", "context-seniority"),
        ("Their customers included Technology firms", "context-domain"), ("The resume describes Dublin collaboration", "context-location"),
        ("They advised an Energy programme", "context-domain"), ("The work involved Financial Services users", "context-project-domain"),
        ("The project supported Retail operations", "context-project-domain"),
    ]
    unsupported = [
        ("They worked with Partner Alpha", "unsupported-relationship"), ("The work occurred in the last three years", "unsupported-temporal"),
        ("They advised Client Beacon", "unsupported-relationship"), ("The person delivered three launches", "unsupported-delivery"),
        ("They worked at Employer Delta", "unsupported-employer"), ("The project achieved a 40 percent uplift", "unsupported-outcome"),
        ("They recently served a public-sector customer", "unsupported-recency"), ("They collaborated with Vendor Echo", "unsupported-relationship"),
        ("The profile records five production deployments", "unsupported-delivery"), ("They advised a London client", "unsupported-relationship"),
        ("Their last engagement ended recently", "unsupported-recency"), ("They delivered a regulated migration", "unsupported-delivery"),
        ("They worked for Customer Foxtrot", "unsupported-employer"), ("The outcome reduced cost by half", "unsupported-outcome"),
        ("They were active between 2019 and 2022", "unsupported-temporal"), ("They advised a Healthcare board", "unsupported-relationship"),
        ("They completed four deployments", "unsupported-delivery"), ("They worked with Group Golf", "unsupported-relationship"),
        ("The last project was in Energy", "unsupported-recency"), ("They achieved an audited result", "unsupported-outcome"),
        ("They delivered a customer portal", "unsupported-delivery"), ("They worked at Company Hotel", "unsupported-employer"),
        ("Their recent assignment involved Retail", "unsupported-recency"), ("They advised a Berlin client", "unsupported-relationship"),
        ("The project met every service target", "unsupported-outcome"),
    ]
    ambiguous = [
        ("Around fifteen years might be relevant", "ambiguous-numeric"), ("Maybe senior, depending on the need", "ambiguous-scope"),
        ("Healthcare or London, unclear priority", "ambiguous-attachment"), ("Not necessarily Financial Services", "ambiguous-negation"),
        ("Principal or senior could work", "ambiguous-role"), ("Roughly ten years, perhaps", "ambiguous-numeric"),
        ("The preference and requirement are not clear", "ambiguous-mandatory"), ("Energy in some sense", "ambiguous-referent"),
        ("Based in London or working with London teams", "ambiguous-attachment"), ("Senior if that means technical leadership", "ambiguous-referent"),
        ("About eight years, give or take", "ambiguous-numeric"), ("Healthcare may refer to the project, not the person", "ambiguous-attachment"),
        ("Possibly Retail, but it is uncertain", "ambiguous-mandatory"), ("The senior requirement is unclear", "ambiguous-scope"),
        ("Around Energy and maybe Technology", "ambiguous-attachment"), ("Could be London-based or London-facing", "ambiguous-attachment"),
        ("Somewhere above ten years", "ambiguous-numeric"), ("The wording leaves exclusion unclear", "ambiguous-negation"),
        ("Senior stakeholders or senior candidates", "ambiguous-role"), ("Perhaps principal, perhaps not", "ambiguous-role"),
        ("Healthcare is mentioned without a clear condition", "ambiguous-scope"), ("Roughly five to ten years", "ambiguous-numeric"),
        ("Maybe exclude Energy, maybe not", "ambiguous-negation"), ("London context could mean location", "ambiguous-attachment"),
        ("A preference may be intended", "ambiguous-mandatory"),
    ]
    groups = [(required, "REQUIRED"), (excluded, "EXCLUDED"), (preferred, "PREFERRED"), (context, "CONTEXT_ONLY"), (unsupported, "UNSUPPORTED"), (ambiguous, "AMBIGUOUS")]
    items=[]; idx=1
    for values, role in groups:
        for entry in values:
            text, family = entry[:2]; field = op = value = None
            if role in {"REQUIRED", "EXCLUDED"}: field, op, value = entry[2:]
            items.append(item(idx, text, role, family, field, op, value)); idx += 1
    mixed = [
        ("At least 15 years and senior search engineers are required", [{"text":"At least 15 years", "role":"REQUIRED", "field":"years_experience", "operator":"gte", "value":15}, {"text":"senior search engineers are required", "role":"REQUIRED", "field":"seniority", "operator":"gte", "value":"senior"}]),
        ("Prefer Healthcare specialists, but exclude junior profiles", [{"text":"Prefer Healthcare specialists", "role":"PREFERRED"}, {"text":"exclude junior profiles", "role":"EXCLUDED", "field":"seniority", "operator":"neq", "value":"junior"}]),
        ("Only London-based principal candidates, excluding Energy", [{"text":"London-based", "role":"REQUIRED", "field":"location", "operator":"eq", "value":"london"}, {"text":"principal candidates", "role":"REQUIRED", "field":"seniority", "operator":"gte", "value":"principal"}, {"text":"excluding Energy", "role":"EXCLUDED", "field":"industry", "operator":"neq", "value":"energy"}]),
        ("A Retail background is preferred; at least 10 years is mandatory", [{"text":"Retail background is preferred", "role":"PREFERRED"}, {"text":"at least 10 years is mandatory", "role":"REQUIRED", "field":"years_experience", "operator":"gte", "value":10}]),
        ("Senior Technology experts with no fewer than 20 years", [{"text":"Senior Technology experts", "role":"REQUIRED", "field":"industry", "operator":"eq", "value":"technology"}, {"text":"no fewer than 20 years", "role":"REQUIRED", "field":"years_experience", "operator":"gte", "value":20}]),
        ("Context includes Healthcare delivery, while London is required", [{"text":"Healthcare delivery", "role":"CONTEXT_ONLY"}, {"text":"London is required", "role":"REQUIRED", "field":"location", "operator":"eq", "value":"london"}]),
        ("Do not include Retail advisers; principal level is preferred", [{"text":"Do not include Retail advisers", "role":"EXCLUDED", "field":"industry", "operator":"neq", "value":"retail"}, {"text":"principal level is preferred", "role":"PREFERRED"}]),
        ("Maybe Energy, but exactly 8 years is required", [{"text":"Maybe Energy", "role":"AMBIGUOUS"}, {"text":"exactly 8 years is required", "role":"REQUIRED", "field":"years_experience", "operator":"eq", "value":8}]),
        ("Advisory work is unsupported; senior Manufacturing is mandatory", [{"text":"Advisory work", "role":"UNSUPPORTED"}, {"text":"senior Manufacturing is mandatory", "role":"REQUIRED", "field":"industry", "operator":"eq", "value":"manufacturing"}]),
        ("A Paris location and Healthcare experience are both required", [{"text":"Paris location", "role":"REQUIRED", "field":"location", "operator":"eq", "value":"paris"}, {"text":"Healthcare experience", "role":"REQUIRED", "field":"industry", "operator":"eq", "value":"healthcare"}]),
    ]
    for text, spans in mixed:
        items.append({"id": f"g3gr-{idx:03d}", "request": text, "pattern_family": "compositional-mixed", "spans": spans, "stratum": "MIXED"}); idx += 1
    return {"benchmark_id":"v0.5.1-staged-interpretation-promotion-v2", "schema_version":"staged-promotion-benchmark-v1", "annotation_policy":"gate3gr-role-policy-v1", "candidate_identity":"deterministic-staged-v2-gate3fr", "registry_id":"v0.5-c1-capability-registry-1", "items":items}


def audit(payload):
    norm=[" ".join(re.findall(r"\w+", x["request"].lower())) for x in payload["items"]]
    families=Counter(x["pattern_family"] for x in payload["items"]); roles=Counter(span["role"] for x in payload["items"] for span in x["spans"])
    token_sets=[set(n.split()) for n in norm]; near_pairs=[]
    for i,j in combinations(range(len(token_sets)),2):
        union=token_sets[i] | token_sets[j]; similarity=(len(token_sets[i] & token_sets[j])/len(union)) if union else 1.0
        if similarity >= 0.85 and norm[i] != norm[j]: near_pairs.append((i,j,round(similarity,3)))
    mixed_rows=sum(len(x["spans"]) > 1 for x in payload["items"])
    return {"rows":len(norm),"unique_normalized":len(set(norm)),"exact_duplicates":len(norm)-len(set(norm)),"pattern_families":dict(families),"largest_family_share":max(families.values())/len(norm),"roles":dict(roles),"near_duplicate_flagged":len(near_pairs),"near_duplicate_pairs":near_pairs[:20],"mixed_rows":mixed_rows,"role_strata":dict(Counter(x.get("stratum", x["spans"][0]["role"]) for x in payload["items"]))}


def main():
    out=Path("tests/fixtures/v051_gate3gr_promotion_v2.json"); payload=build(); out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); print(json.dumps({"audit":audit(payload),"sha256":hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))


if __name__ == "__main__": main()
