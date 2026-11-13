import ast 

def same_structure(code1, code2):
    tree1 = ast.dump(ast.parse(code1), include_attributes=False)
    tree2 = ast.dump(ast.parse(code2), include_attributes=False)

    return tree1 == tree2
def duplicate_reason(candidate, source, attempt_history):
    if same_structure(candidate, source):
        return "Candidate is unchanged from original source"
    for entry in attempt_history:
        if entry["candidate"] is not None:
            if same_structure(candidate, entry["candidate"]):
                return f"Duplicate of attempt {entry['attempt']}"

    return None