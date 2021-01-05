#Recipe for building application in RDK Platform
DESCRIPTION = "Honeyd application"
LICENSE = "CLOSED"

#Commit id
SRCREV = ""
#Source file version control url
SRC_URI = ""
S = "${WORKDIR}/git"


DEPENDS= "libdnet libevent libpcap libpcre libedit zlib ${@bb.utils.contains('DISTRO_FEATURES', 'cpg-ecfs', 'cpgc', 'cpg-libs', d)}"
inherit autotools pkgconfig systemd

CFLAGS += "-DPROD_LABELS"
LDFLAGS+= "-L${STAGING_DIR_TARGET}/lib -ldl -L${STAGING_DIR_TARGET}/usr/lib -levent"
EXTRA_OECONF += "--prefix=${STAGING_DIR_TARGET}/usr"
EXTRA_OECONF += "--with-libdnet=${STAGING_DIR_TARGET}/usr"

do_install_append () {
        install -d ${D}${bindir}
        install -m 0755  ${S}/service-scripts/script.sh ${D}${bindir}
        install -m 0755  ${S}/service-scripts/start_honeyd.sh ${D}${bindir}
        install -d ${D}${systemd_unitdir}/system
        install -m 0644 ${S}/service-scripts/config_receiver.service ${D}${systemd_unitdir}/system
        install -m 0644 ${S}/service-scripts/inotify-decepgate.service ${D}${systemd_unitdir}/system
        install -m 0644 ${S}/service-scripts/start-honeyd.service ${D}${systemd_unitdir}/system
        install -m 0644 ${S}/service-scripts/start-honeyd.timer ${D}${systemd_unitdir}/system

}

FILES_${PN} += "${systemd_unitdir}/system/config_receiver.service ${systemd_unitdir}/system/inotify-decepgate.service ${systemd_unitdir}/system/start-honeyd.service ${systemd_unitdir}/system/start-honeyd.timer"
SYSTEMD_SERVICE_${PN} = "config_receiver.service"
SYSTEMD_SERVICE_${PN} += "inotify-decepgate.service"
SYSTEMD_SERVICE_${PN} += "start-honeyd.service"
SYSTEMD_SERVICE_${PN} += "start-honeyd.timer"
