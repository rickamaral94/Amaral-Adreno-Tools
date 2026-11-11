/*
 * Minimal read-only KGSL device-info probe for Android/AArch64.
 *
 * It performs only KGSL_PROP_DEVICE_INFO, the same property Turnip reads in
 * tu_knl_kgsl.cc. It does not allocate GPU memory or submit work.
 */
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define KGSL_IOC_TYPE 0x09
#define KGSL_PROP_DEVICE_INFO 0x1

struct kgsl_devinfo {
    unsigned int device_id;
    unsigned int chip_id;
    unsigned int mmu_enabled;
    unsigned long gmem_gpubaseaddr;
    unsigned int gpu_id;
    size_t gmem_sizebytes;
};

struct kgsl_device_getproperty {
    unsigned int type;
    void *value;
    size_t sizebytes;
};

#define IOCTL_KGSL_DEVICE_GETPROPERTY \
    _IOWR(KGSL_IOC_TYPE, 0x2, struct kgsl_device_getproperty)

int main(void)
{
    int fd = open("/dev/kgsl-3d0", O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "open(/dev/kgsl-3d0): %s\n", strerror(errno));
        return 2;
    }

    struct kgsl_devinfo info = {0};
    struct kgsl_device_getproperty prop = {
        .type = KGSL_PROP_DEVICE_INFO,
        .value = &info,
        .sizebytes = sizeof(info),
    };

    if (ioctl(fd, IOCTL_KGSL_DEVICE_GETPROPERTY, &prop) != 0) {
        fprintf(stderr, "KGSL_PROP_DEVICE_INFO: %s\n", strerror(errno));
        close(fd);
        return 3;
    }
    close(fd);

    const unsigned int turnip_gpu_id =
        ((info.chip_id >> 24) & 0xffU) * 100U +
        ((info.chip_id >> 16) & 0xffU) * 10U +
        ((info.chip_id >> 8) & 0xffU);

    printf(
        "{\"schema\":1,"
        "\"source\":\"KGSL_PROP_DEVICE_INFO\","
        "\"device_id\":%u,"
        "\"chip_id\":\"0x%08x\","
        "\"mmu_enabled\":%u,"
        "\"kgsl_gpu_id\":%u,"
        "\"turnip_derived_gpu_id\":%u,"
        "\"gmem_gpubaseaddr\":\"0x%lx\","
        "\"gmem_sizebytes\":%zu}\n",
        info.device_id,
        info.chip_id,
        info.mmu_enabled,
        info.gpu_id,
        turnip_gpu_id,
        info.gmem_gpubaseaddr,
        info.gmem_sizebytes
    );
    return 0;
}
