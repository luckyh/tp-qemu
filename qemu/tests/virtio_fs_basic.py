import logging

from virttest import error_context
from virttest import utils_misc


@error_context.context_aware
def run(test, params, env):
    """
    KVM boot time test:
    1) Set init run level to 1
    2) Send a shutdown command to the guest, or issue a system_powerdown
       monitor command (depending on the value of shutdown_method)
    3) Boot up the guest and measure the boot time
    4) set init run level back to the old one

    :param test: QEMU test object
    :param params: Dictionary with the test parameters
    :param env: Dictionary with test environment
    """

    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login()

    fs_list = params.objects("filesystems")
    for fs in fs_list:
        fs_params = params.object_params(fs)
        fs_tag = fs_params["fs_target"]
        fs_dest = "/run/virtiofs_test/%s" % fs_tag

        error_context.context("Mount virtiofs target '%s' in guest" % fs_tag,
                              logging.info)
        mkdir_cmd = "mkdir -p %s" % fs_dest
        session.cmd(mkdir_cmd)
        mount_cmd = "mount -t virtiofs %s %s" % (fs_tag, fs_dest)
        session.cmd(mount_cmd)

        error_context.context("Creating files under target '%s'" % fs_tag,
                              logging.info)
        session.cmd("echo abc123 > %s/test_file" % fs_dest)

        error_context.context("Umount target '%s'" % fs_tag, logging.info)
        session.cmd("umount %s" % fs_dest)
