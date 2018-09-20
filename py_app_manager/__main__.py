''' Run ./manage from repo root to use the management console
'''

import sys, os, json, logging, subprocess
logging.basicConfig(level=logging.INFO)

from contextlib import suppress
try:
    from git import Repo
except ImportError as e:
    Repo = None
repo = None

from py_app_manager.pre_deps import *
from py_app_manager.cmd_runner import CmdRunner

_deps_updated = False
def ensure_deps(force=False):
    global _deps_updated, repo
    if (force or not deps_up_to_date()) and not _deps_updated:
        def install_deps():
            must_run("python3 -m pip install -r requirements.txt")
            must_run("npm i")
            must_run("npx lerna bootstrap")
            set_deps_up_to_date()
        if Repo is not None:
            repo = Repo('./')
            if repo.is_dirty():
                logging.warning("⚠️ Repository is dirty; skipping reinstall of requirements!")
            else:
                logging.warning("⚠️ Detected repository but not dirty; installing requirements!")
                install_deps()
        else:
            install_deps()
        _deps_updated = True


def export(env_name, env_value):
    os.environ[env_name] = env_value


# check we're in the correct directory
try:
    with open('package.json', 'r') as f:
        pkg_file = json.load(f)
        assert pkg_file['name'] == "root"
        assert os.path.isdir("./packages/api")
        assert os.path.isdir("./packages/lib")
        assert os.path.isdir("./packages/ui")
except Exception as e:
    print("Please run ./manage from the root directory (of the repository)")
    sys.exit(255)


skip_ensure_deps = len(sys.argv) > 1 and ( \
        sys.argv[1] == "mgr_set_up_to_date" \
        or False
    )
_deps_updated = skip_ensure_deps


# ensure deps and things are installed before we go further
try:
    # ensure_venv()
    ensure_deps()
except Exception as e:
    print("unable to install dependencies; exiting")
    print(e, e.args, e.message)
    raise e


# main UI


import click
stage_option = click.option('--stage', type=click.Choice(['prod', 'staging', 'dev']), default='dev')
type_pkg_choice = click.Choice(['api', 'ui', 'lib', 'all'])

@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug mode enabled")


@cli.command()
def reinstall():
    ensure_deps(force=True)


@cli.command()
def clean():
    # clean up any temporary / boring files
    cmds = [
        "rm -rf ./.flux-dev.*.log*"
    ]
    logging.debug("Cleaning up...")
    for cmd in cmds:
        logging.debug("Running %s" % cmd)
        must_run(cmd)
    logging.debug("Done cleaning up.")


@cli.command()
@click.argument('pkgs', nargs=-1)
@click.pass_context
def mgr_add_dep(ctx, pkgs):
    logging.debug("Packages to install: %s" % list(pkgs))
    if len(pkgs) == 0:
        logging.error("No packages supplied to install. Exiting.")
        sys.exit(1)
    run_or("python3 -m pip install %s" % (' '.join(pkgs) or '',), 'Unable to install packages: %s' % (pkgs,))
    logging.info("Installed packages: %s" % list(pkgs))
    must_run("python3 -m pip freeze > requirements.txt")
    logging.info("Saved `requirements.txt`")


@cli.command()
def mgr_set_up_to_date():
    set_deps_up_to_date()


def install_npm_deps(target, deps, dev=False):
    logging.warning("⚠️ dependencies will be installed one at a time. (It's a lerna thing)")
    runner = CmdRunner(must_run)
    lerna_pkg = '' if target == 'all' else target
    dev_flag = "--dev" if dev else ""
    for d in deps:
        runner.add('Installing node dependency `{d}` for `{pkg}`'.format(d=d, pkg=target), 'npx lerna add {d} {pkg} {dev}'.format(d=d, pkg=lerna_pkg, dev=def_flag))
    runner.run()


@cli.command()
@click.argument('target', nargs=1, type=type_pkg_choice)  # help='Package to add dependency to',
@click.argument('dependencies', nargs=-1)  # help='NPM packages to add as dependencies'
@click.option('--dev', default=False, type=bool, help="Install as devDependency")
def addto(target, dependencies, dev):
    install_npm_deps(target, dependencies, dev)


@cli.command()
@click.argument('dependencies', nargs=-1)  # help='NPM packages to add as dependencies'
@click.option('--dev', default=False, type=bool, help="Install as devDependency")
def add(dependencies, dev):
    install_npm_deps('all', dependencies, dev)


@cli.command()
@stage_option
@click.argument('target', nargs=1, type=click.Choice(['api', 'ui', 'all']))
@click.argument('args', nargs=-1)
def test(stage, target, args):
    export("STAGE", stage)
    runner = CmdRunner(must_run)
    if target in {'api', 'all'}:
        runner.add('api tests', 'cd packages/api && npm run test -- --stage {s} {args}'.format(s=stage, args=' '.join(args)))
    runner.run()


@cli.command()
@stage_option
@click.option('--skip-tests', default=False, type=bool)
@click.argument('target', nargs=1, type=click.Choice(['api']))
@click.argument('args', nargs=-1)
def deploy(stage, skip_tests, target, args):
    runner = CmdRunner(must_run)
    if target in {'api', 'all'}:
        runner.add('api', "cd packages/api && node_modules/.bin/sls deploy --stage {} {args}".format(stage, args=' '.join(args)))
    runner.run()


@cli.command()
@click.argument('target', nargs=1, type=click.Choice(['ui', 'api', 'all']))
@stage_option
def build(target, stage):
    export("STAGE", stage)
    logging.info("Building {} for {}".format(target, stage))

    try:
        if stage == "prod":
            logging.info("Building for prod!")
            if 'IS_NETLIFY' in os.environ:
                logging.info("Checking out most recent version tag")
                must_run("git reset --hard HEAD && git checkout {}".format(os.environ['MOST_RECENT_TAG']))
            else:
                logging.info("Not on netlify - will not checkout most recent git tag")

        def build_ui():
            logging.info("### BUILDING UI ###")
            must_run("cd packages/ui && npm run build")

        def build_api():
            logging.info("### BUILDING API ###")
            must_run("cd packages/api && npm run build --stage {stage}".format(stage=stage))

        def build_all():
            build_ui()
            build_api()

        return ({
            'ui': build_ui,
            'api': build_api,
            'all': build_all
        }[target])()
    finally:
        pass


@cli.command()
@click.argument('dev_target', type=click.Choice(['ui', 'api', 'all']))
@stage_option
def dev(dev_target, stage):
    # # first check dynamodb install
    # if dev_target in {'api', 'all'}:
    #     # we need to ensure dynamodb is installed for API dev (note: currently not _actually_ required for anything... -- 9/9/2018)
    #     must_run("cd packages/api && node_modules/.bin/sls dynamodb install")

    # `--stage` has special meaning with dev cmd (emulates a stage via api points (UI))
    os.environ["STAGE"] = "dev"

    import libtmux
    api_port = 52700
    ui_port = 32710
    server = libtmux.Server(socket_name='flux-app-tmux-session')

    def kill_sessions():
        with suppress(Exception):
            for s in server.list_sessions():
                s.kill_session()

    kill_sessions()
    session = None
    window = None
    log_files = []

    def run_dev_cmd(dir, cmd, name, active_pane=None, vertical=False):
        nonlocal session, window, log_files
        (to_run, l) = cmd_w_log(cmd, name, dir_offset='../../')
        to_run = "printf '\033]2;%s\033\\' '{title}'; ".format(title=name) + to_run
        to_run += "; echo -e '\\n\\n' && /usr/bin/read -p 'Press enter to terminate all...' && tmux kill-session -t main"
        log_files.append(l)
        if session is None:
            session = server.new_session(session_name="main", start_directory=dir, window_command=to_run)
            session.set_option('mouse', 'on')
            # session.set_option('remain-on-exit', 'on')
            window = session.list_windows()[0]
            return window.attached_pane
        else:
            opts = {} if active_pane is None else {'target': active_pane.id}
            return window.split_window(start_directory=dir, shell=to_run, vertical=vertical, **opts)

    # uncomment the below if we need to compile flux-lib
    lib_pane = run_dev_cmd('./packages/lib', 'npm run watch', 'dev-lib')
    if dev_target in {'ui', 'all'}:
        ui_pane = run_dev_cmd('./packages/ui', "STAGE={} npm run serve".format(stage), 'dev-ui')

    if dev_target in {'api', 'all'}:
        # mongo dev server port: 53799
        mongo_pane = run_dev_cmd('./packages/api', 'npm run mongo-dev', "mongo-dev", vertical=False)
        api_cmd = "npm run watch -- --stage dev --port %d" % (api_port,)
        api_pane = run_dev_cmd('./packages/api', api_cmd, "dev-api", vertical=True, active_pane=mongo_pane)
        # don't need to run tsc on the api atm
        # compile_pane = run_dev_cmd('./packages/api', 'npm run watch:build', 'api-watch', vertical=True)

    window.select_layout('tiled')

    session.attach_session()
    kill_sessions()
    print("Log files: ", ', '.join(log_files))


# monkey patch so usage output looks nicer
sys.argv[0] = './manage'
cli()
