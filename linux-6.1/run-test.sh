#!/bin/bash

KERNEL="linux-6.1/arch/x86/boot/bzImage"
INITRD="rootfs.cpio.gz"

# Check files exist
if [ ! -f "$KERNEL" ]; then
    echo "ERROR: Kernel not found: $KERNEL"
    exit 1
fi

if [ ! -f "$INITRD" ]; then
    echo "ERROR: Initrd not found: $INITRD"
    exit 1
fi

echo "========================================="
echo "  Testing changes to Linux Kernel! :)"
echo "========================================="

sudo qemu-system-x86_64 \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -append "console=ttyS0 rdinit=/init" \
    -nographic \
    -m 512M \
    -smp 2

# Key change: "rdinit=/init" tells kernel to run /init from initramfs
# NOT "root=/dev/..." which looks for a disk
