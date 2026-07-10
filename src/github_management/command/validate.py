from .utils import load_github_management_yaml

def validate(args) -> None:
    """
    Validate a YAML file for syntax and consistency.
    """
    try:
        load_github_management_yaml(args.file)
        print(f"[validate] File {args.file} is valid.")
    except Exception as e:
        print(f"[validate] Error validating file {args.file}: {e}")
