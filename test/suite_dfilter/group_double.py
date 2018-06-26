# Copyright (c) 2013 by Gilbert Ramirez <gram@alumni.rice.edu>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from suite_dfilter import dfiltertest

class case_double(dfiltertest.DFTestCase):

    trace_file = "ntp.pcap"

    def test_eq_1(self):
        dfilter = "ntp.rootdelay == 0.0626983642578125"
        self.assertDFilterCount(dfilter, 1)

    def test_eq_2(self):
        dfilter = "ntp.rootdelay == 0.0626"
        self.assertDFilterCount(dfilter, 0)

    def test_gt_1(self):
        dfilter = "ntp.rootdelay > 1.0626"
        self.assertDFilterCount(dfilter, 0)

    def test_gt_2(self):
        dfilter = "ntp.rootdelay >  0.0626983642578125"
        self.assertDFilterCount(dfilter, 0)

    def test_gt_3(self):
        dfilter = "ntp.rootdelay >  0.0026"
        self.assertDFilterCount(dfilter, 1)

    def test_ge_1(self):
        dfilter = "ntp.rootdelay >= 1.0026"
        self.assertDFilterCount(dfilter, 0)

    def test_ge_2(self):
        dfilter = "ntp.rootdelay >=  0.0626983642578125"
        self.assertDFilterCount(dfilter, 1)

    def test_ge_3(self):
        dfilter = "ntp.rootdelay >=  0.0026"
        self.assertDFilterCount(dfilter, 1)

    def test_lt_1(self):
        dfilter = "ntp.rootdelay < 1.0026"
        self.assertDFilterCount(dfilter, 1)

    def test_lt_2(self):
        dfilter = "ntp.rootdelay <  0.0626983642578125"
        self.assertDFilterCount(dfilter, 0)

    def test_lt_3(self):
        dfilter = "ntp.rootdelay <  0.0026"
        self.assertDFilterCount(dfilter, 0)

    def test_le_1(self):
        dfilter = "ntp.rootdelay <= 1.0026"
        self.assertDFilterCount(dfilter, 1)

    def test_le_2(self):
        dfilter = "ntp.rootdelay <=  0.0626983642578125"
        self.assertDFilterCount(dfilter, 1)

    def test_le_3(self):
        dfilter = "ntp.rootdelay <=  0.0026"
        self.assertDFilterCount(dfilter, 0)
