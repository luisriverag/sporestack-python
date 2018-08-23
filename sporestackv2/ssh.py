from paramiko import SSHClient, AutoAddPolicy
from .paramiko_interactive import interactive_shell


def ssh(hostname, command, stdin=None, interactive=False, port=1060):
    """
    FIXME: This won't fail out on non-zero exit statuses.
    FIXME: Consider different key poliy?
    """
    if not isinstance(hostname, str):
        raise TypeError('hostname must be string')
    if stdin is not None and interactive is True:
        raise ValueError('Cannot use stdin with interactive.')
    with SSHClient() as ssh_client:
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=hostname,
                           port=port,
                           username='vmmanagement',
                           password='',
                           allow_agent=False,
                           look_for_keys=False)
        if interactive is False:
            ssh_stdin, stdout, stderr = ssh_client.exec_command(command)
            if stdin is not None:
                ssh_stdin.write(stdin)
                ssh_stdin.flush()
                ssh_stdin.channel.shutdown_write()
            # Kinda hacky, but works.
            return_code = ssh_stdin.channel.recv_exit_status()
            return stdout.read(), stderr.read(), return_code
        else:
            channel = ssh_client.get_transport().open_session()
            channel.get_pty()
            channel.exec_command(command)
            interactive_shell(channel)
            channel.close()
            ssh_client.close()
