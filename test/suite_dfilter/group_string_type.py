# Copyright (c) 2013 by Gilbert Ramirez <gram@alumni.rice.edu>
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-2.0-or-later

from suite_dfilter import dfiltertest

class case_string(dfiltertest.DFTestCase):
    trace_file = "http.pcap"

    def test_eq_1(self):
        dfilter = 'http.request.method == "HEAD"'
        self.assertDFilterCount(dfilter, 1)

    def test_eq_2(self):
        dfilter = 'http.request.method == "POST"'
        self.assertDFilterCount(dfilter, 0)

    def test_gt_1(self):
        dfilter = 'http.request.method > "HEAC"'
        self.assertDFilterCount(dfilter, 1)

    def test_gt_2(self):
        dfilter = 'http.request.method > "HEAD"'
        self.assertDFilterCount(dfilter, 0)

    def test_gt_3(self):
        dfilter = 'http.request.method > "HEAE"'
        self.assertDFilterCount(dfilter, 0)

    def test_ge_1(self):
        dfilter = 'http.request.method >= "HEAC"'
        self.assertDFilterCount(dfilter, 1)

    def test_ge_2(self):
        dfilter = 'http.request.method >= "HEAD"'
        self.assertDFilterCount(dfilter, 1)

    def test_ge_3(self):
        dfilter = 'http.request.method >= "HEAE"'
        self.assertDFilterCount(dfilter, 0)

    def test_lt_1(self):
        dfilter = 'http.request.method < "HEAC"'
        self.assertDFilterCount(dfilter, 0)

    def test_lt_2(self):
        dfilter = 'http.request.method < "HEAD"'
        self.assertDFilterCount(dfilter, 0)

    def test_lt_3(self):
        dfilter = 'http.request.method < "HEAE"'
        self.assertDFilterCount(dfilter, 1)

    def test_le_1(self):
        dfilter = 'http.request.method <= "HEAC"'
        self.assertDFilterCount(dfilter, 0)

    def test_le_2(self):
        dfilter = 'http.request.method <= "HEAD"'
        self.assertDFilterCount(dfilter, 1)

    def test_le_3(self):
        dfilter = 'http.request.method <= "HEAE"'
        self.assertDFilterCount(dfilter, 1)

    def test_slice_1(self):
        dfilter = 'http.request.method[0] == "H"'
        self.assertDFilterCount(dfilter, 1)

    def test_slice_2(self):
        dfilter = 'http.request.method[0] == "P"'
        self.assertDFilterCount(dfilter, 0)

    def test_slice_3(self):
        dfilter = 'http.request.method[0:4] == "HEAD"'
        self.assertDFilterCount(dfilter, 1)

    def test_slice_4(self):
        dfilter = 'http.request.method[0:4] != "HEAD"'
        self.assertDFilterCount(dfilter, 0)

    def test_slice_5(self):
        dfilter = 'http.request.method[1:2] == "EA"'
        self.assertDFilterCount(dfilter, 1)

    def test_slice_6(self):
        dfilter = 'http.request.method[1:2] > "EA"'
        self.assertDFilterCount(dfilter, 0)

    def test_slice_7(self):
        dfilter = 'http.request.method[-1] == "D"'
        self.assertDFilterCount(dfilter, 1)

    def test_slice_8(self):
        dfilter = 'http.request.method[-2] == "D"'
        self.assertDFilterCount(dfilter, 0)

    def xxxtest_stringz_1(self):
            return self.DFilterCount(pkt_tftp,
                    'tftp.type == "octet"', 1)

    def xxxtest_stringz_2(self):
            return self.DFilterCount(pkt_tftp,
                    'tftp.type == "junk"', 0)

    def test_contains_1(self):
        dfilter = 'http.request.method contains "E"'
        self.assertDFilterCount(dfilter, 1)

    def test_contains_2(self):
        dfilter = 'http.request.method contains "EA"'
        self.assertDFilterCount(dfilter, 1)

    def test_contains_3(self):
        dfilter = 'http.request.method contains "HEAD"'
        self.assertDFilterCount(dfilter, 1)

    def test_contains_4(self):
        dfilter = 'http.request.method contains "POST"'
        self.assertDFilterCount(dfilter, 0)

    def test_contains_5(self):
        dfilter = 'http.request.method contains 50:4f:53:54' # "POST"
        self.assertDFilterCount(dfilter, 0)

    def test_contains_6(self):
        dfilter = 'http.request.method contains 48:45:41:44' # "HEAD"
        self.assertDFilterCount(dfilter, 1)

    def test_contains_fail_0(self):
        dfilter = 'http.user_agent contains "update"'
        self.assertDFilterCount(dfilter, 0)

    def test_contains_fail_1(self):
        dfilter = 'http.user_agent contains "UPDATE"'
        self.assertDFilterCount(dfilter, 0)

    def test_contains_upper_0(self):
        dfilter = 'upper(http.user_agent) contains "UPDATE"'
        self.assertDFilterCount(dfilter, 1)

    def test_contains_upper_1(self):
        dfilter = 'upper(http.user_agent) contains "update"'
        self.assertDFilterCount(dfilter, 0)

    def test_contains_upper_2(self):
        dfilter = 'upper(tcp.seq) == 4'
        self.assertDFilterFail(dfilter)

    def test_contains_lower_0(self):
        dfilter = 'lower(http.user_agent) contains "UPDATE"'
        self.assertDFilterCount(dfilter, 0)

    def test_contains_lower_1(self):
        dfilter = 'lower(http.user_agent) contains "update"'
        self.assertDFilterCount(dfilter, 1)

    def test_eq_lower_1(self):
        dfilter = 'lower(tcp.seq) == 4'
        self.assertDFilterFail(dfilter)

    def test_string_len(self):
        dfilter = 'len(http.request.method) == 4'
        self.assertDFilterCount(dfilter, 1)

    def test_eq_unicode(self):
        dfilter = 'tcp.flags.str == "·······AP···"'
        self.assertDFilterCount(dfilter, 1)

    def test_contains_unicode(self):
        dfilter = 'tcp.flags.str contains "·······AP···"'
        self.assertDFilterCount(dfilter, 1)
