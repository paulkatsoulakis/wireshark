#!/usr/pkg/bin/bash
# Setup development environment on BSD-like platforms.
#
# Tested on: FreeBSD, OpenBSD, NetBSD.
#
# Wireshark - Network traffic analyzer
# By Gerald Combs <gerald@wireshark.org>
# Copyright 1998 Gerald Combs
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
# We drag in tools that might not be needed by all users; it's easier
# that way.
#

if [ "$1" = "--help" ]
then
	echo "\nUtility to setup a bsd-based system for Wireshark Development.\n"
	echo "The basic usage installs the needed software\n\n"
	echo "Usage: $0 [--install-optional] [...other options...]\n"
	echo "\t--install-optional: install optional software as well"
	echo "\t[other]: other options are passed as-is to pkg manager.\n"
	exit 1
fi

# Check if the user is root
if [ $(id -u) -ne 0 ]
then
	echo "You must be root."
	exit 1
fi

for op
do
	if [ "$op" = "--install-optional" ]
	then
		ADDITIONAL=1
	else
		OPTIONS="$OPTIONS $op"
	fi
done

BASIC_LIST="\
	cmake \
	qt5 \
	git"

ADDITIONAL_LIST="\
	gettext-tools \
	snappy \
	bcg729 \
	doxygen \
	libssh \
	libmaxminddb \
	libsmi"

# Guess which package manager we will use
PM=`which pkgin 2> /dev/null || which pkg 2> /dev/null || which pkg_add 2> /dev/null`

case $PM in
	*/pkgin)
		PM_OPTIONS="install"
		PM_SEARCH="pkgin search"
		;;
	*/pkg)
		PM_OPTIONS="install"
		PM_SEARCH="pkg search"
		;;
	*/pkg_add)
		PM_OPTIONS=""
		PM_SEARCH="pkg_info"
		;;
esac


echo "Using $PM ($PM_SEARCH)"

# Adds package $2 to list variable $1 if the package is found
add_package() {
	local list="$1" pkgname="$2"

	# fail if the package is not known
	$PM_SEARCH "$pkgname" >& /dev/null || return 1

	# package is found, append it to list
	eval "${list}=\"\${${list}} \${pkgname}\""
}

# pkg-config: NetBSD
add_package BASIC_LIST pkg-config ||
echo "pkg-config is unavailable"

# c-ares: FreeBSD
# libcares: OpenBSD
add_package ADDITIONAL_LIST c-ares ||
add_package ADDITIONAL_LIST libcares ||
echo "c-ares is unavailable"

# rubygem-asciidoctor: FreeBSD
add_package ADDITIONAL_LIST rubygem-asciidoctor ||
echo "asciidoctor is unavailable"

# lz4: NetBSD
add_package ADDITIONAL_LIST lz4 ||
echo "lz4 is unavailable"

# nghttp2: NetBSD
add_package ADDITIONAL_LIST nghttp2 ||
echo "nghttp2 is unavailable"

# json-glib: NetBSD
add_package ADDITIONAL_LIST json-glib ||
echo "json-glib is unavailable"

# spandsp: NetBSD
add_package ADDITIONAL_LIST spandsp ||
echo "spandsp is unavailable"

# ninja: FreeBSD, OpenBSD
# ninja-build: NetBSD
add_package ADDITIONAL_LIST ninja-build ||
add_package ADDITIONAL_LIST ninja ||
echo "ninja is unavailable"

# Add OS-specific required/optional packages
# Those not listed don't require additions.
case `uname` in
	OpenBSD)
		add_package ADDITIONAL_LIST bison || echo "bison is unavailable"
		;;
	NetBSD)
		add_package ADDITIONAL_LIST libgcrypt || echo "libgcrypt is unavailable"
		;;
esac

ACTUAL_LIST=$BASIC_LIST

# Now arrange for optional support libraries
if [ $ADDITIONAL ]
then
	ACTUAL_LIST="$ACTUAL_LIST $ADDITIONAL_LIST"
fi

$PM $PM_OPTIONS $ACTUAL_LIST $OPTIONS
if [ $? != 0 ]
then
	exit 2
fi

if [ ! $ADDITIONAL ]
then
	echo "\n*** Optional packages not installed. Rerun with --install-optional to have them.\n"
fi
