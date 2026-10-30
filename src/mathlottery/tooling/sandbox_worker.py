"""Linux worker: Landlock filesystem allowlist, seccomp and resource limits.

Launched using Python -I with a scrubbed environment. Never import this to execute code
in the harness process. Unsupported isolation fails closed (exit code 78).
"""

import ctypes
import errno
import json
import math
import os
import platform
import resource
import sys
from pathlib import Path


def isolate(workspace: Path, memory_mb: int, seconds: float, output_limit: int) -> None:
    if sys.platform != "linux" or platform.machine() not in ("x86_64", "aarch64"):
        raise RuntimeError("Linux x86_64/aarch64 with Landlock and libseccomp is required")
    libc = ctypes.CDLL(None, use_errno=True)
    seccomp = ctypes.CDLL("libseccomp.so.2", use_errno=True)
    abi = libc.syscall(444, 0, 0, 1)
    if abi < 1:
        raise RuntimeError("Landlock is unavailable in this kernel")

    class Ruleset(ctypes.Structure):
        _fields_ = [("handled_access_fs", ctypes.c_uint64)]

    class PathRule(ctypes.Structure):
        _pack_ = 1
        _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]

    handled = (1 << 13) - 1
    if abi >= 2:
        handled |= 1 << 13
    if abi >= 3:
        handled |= 1 << 14
    ruleset = Ruleset(handled)
    fd = libc.syscall(444, ctypes.byref(ruleset), ctypes.sizeof(ruleset), 0)
    if fd < 0:
        raise OSError(ctypes.get_errno(), "landlock_create_ruleset")

    def allow(path, access):
        path = Path(path).resolve()
        if not path.exists():
            return
        if path.is_file() or not path.is_dir():
            access &= (1 << 0) | (1 << 1) | (1 << 2) | (1 << 14)
        parent_fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
        try:
            rule = PathRule(access & handled, parent_fd)
            if libc.syscall(445, fd, 1, ctypes.byref(rule), 0):
                raise OSError(ctypes.get_errno(), "landlock_add_rule")
        finally:
            os.close(parent_fd)

    try:
        read = (1 << 0) | (1 << 2) | (1 << 3)
        for path in {"/usr", "/lib", "/lib64", sys.prefix, sys.base_prefix}:
            allow(path, read)
        allow("/dev/null", (1 << 1) | (1 << 2))
        allow("/dev/urandom", 1 << 2)
        allow(workspace, handled)
        if libc.prctl(38, 1, 0, 0, 0) or libc.syscall(446, fd, 0):
            raise OSError(ctypes.get_errno(), "landlock_restrict_self")
    finally:
        os.close(fd)

    seccomp.seccomp_init.argtypes = [ctypes.c_uint32]
    seccomp.seccomp_init.restype = ctypes.c_void_p
    seccomp.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    seccomp.seccomp_syscall_resolve_name.restype = ctypes.c_int
    seccomp.seccomp_rule_add.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
    ]
    seccomp.seccomp_load.argtypes = [ctypes.c_void_p]
    seccomp.seccomp_release.argtypes = [ctypes.c_void_p]
    context = seccomp.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    if not context:
        raise RuntimeError("seccomp_init failed")
    # Metadata/truncation syscalls also cover filesystem operations absent in Landlock ABI 1.
    blocked = """socket socketpair connect bind listen accept accept4 sendto sendmsg recvmsg
        execve execveat fork vfork clone clone3 ptrace process_vm_readv process_vm_writev
        kill tkill tgkill pidfd_open pidfd_getfd pidfd_send_signal
        mount umount2 pivot_root chroot unshare setns bpf perf_event_open
        init_module finit_module delete_module reboot kexec_load open_by_handle_at
        name_to_handle_at io_uring_setup userfaultfd keyctl add_key request_key
        chmod fchmod fchmodat fchmodat2 chown fchown lchown fchownat
        truncate ftruncate utime utimes futimesat utimensat
        link linkat symlink symlinkat mknod mknodat
        setxattr lsetxattr fsetxattr removexattr lremovexattr fremovexattr""".split()
    try:
        for name in blocked:
            number = seccomp.seccomp_syscall_resolve_name(name.encode())
            if number >= 0 and seccomp.seccomp_rule_add(
                context, 0x00050000 | errno.EPERM, number, 0
            ):
                raise RuntimeError(f"Cannot block syscall {name}")
        if seccomp.seccomp_load(context):
            raise RuntimeError("seccomp_load failed")
    finally:
        seccomp.seccomp_release(context)
    resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(seconds), math.ceil(seconds) + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (max(1000000, output_limit * 4),) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    payload = json.loads(sys.stdin.read())
    code = payload["code"]
    try:
        isolate(Path.cwd(), payload["memory_mb"], payload["seconds"], payload["output_limit"])
    except Exception as error:
        print(f"ISOLATION_UNAVAILABLE: {error}", file=sys.stderr)
        return 78
    exec(compile(code, "<mathlottery-experiment>", "exec"), {"__name__": "__main__"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
