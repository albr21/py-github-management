import sys
from .client import Client
from .cli import build_cli

from .command.validate import validate
from .command.extract import extract
from .command.diff import diff
from .command.create.create_repo import create_repo
from .command.push.user.topics import push_user_topics
from .command.push.user.cleanup import push_user_cleanup
from .command.push.org.topics import push_org_topics
from .command.push.org.teams import push_org_teams
from .command.push.org.cleanup import push_org_cleanup

def push_user_parser(client: Client, args) -> None:
    target_handlers = {
        "topics": push_user_topics,
        "cleanup": push_user_cleanup,
    }

    handler = target_handlers.get(args.push_target)
    if handler:
        handler(client, args)
    else:
        print(f"Unknown push target: {args.push_target}")
        sys.exit(1)

def push_org_parser(client: Client, args) -> None:
    target_handlers = {
        "topics": push_org_topics,
        "teams": push_org_teams,
        "cleanup": push_org_cleanup,
    }

    handler = target_handlers.get(args.push_target)
    if handler:
        handler(client, args)
    else:
        print(f"Unknown push target: {args.push_target}")
        sys.exit(1)

def main():
    parser = build_cli()
    args = parser.parse_args()

    # Commands that don't need a GitHub client
    if args.command in ("validate", "v"):
        validate(args)
        return

    # All other commands need a GitHub client
    client = Client(base_url="https://api.github.com")

    if args.command in ("extract", "e"):
        extract(client, args)

    elif args.command in ("diff", "d"):
        diff(client, args)

    elif args.command in ("create", "c"):
        create_handlers = {
            "repo": create_repo,
        }
        handler = create_handlers.get(args.create_target)
        if handler:
            handler(client, args)
        else:
            parser.print_help()
            sys.exit(1)

    elif args.command in ("push", "p"):
        push_scope_handlers = {
            "org": push_org_parser,
            "user": push_user_parser,
        }

        scope_handler = push_scope_handlers.get(args.push_scope)
        if scope_handler:
            scope_handler(client, args)
        else:
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()
