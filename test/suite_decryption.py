#
# -*- coding: utf-8 -*-
# Wireshark tests
# By Gerald Combs <gerald@wireshark.org>
#
# Ported from a set of Bash scripts which were copyright 2005 Ulf Lamping
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
'''Decryption tests'''

import config
import os.path
import subprocesstest
import unittest

class case_decrypt_80211(subprocesstest.SubprocessTestCase):
    def test_80211_wpa_psk(self):
        '''IEEE 802.11 WPA PSK'''
        # https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=view&target=wpa-Induction.pcap
        capture_file = os.path.join(config.capture_dir, 'wpa-Induction.pcap.gz')
        self.runProcess((config.cmd_tshark,
                '-o', 'wlan.enable_decryption: TRUE',
                '-Tfields',
                '-e', 'http.request.uri',
                '-r', capture_file,
                '-Y', 'http',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('favicon.ico'))

    def test_80211_wpa_eap(self):
        '''IEEE 802.11 WPA EAP (EAPOL Rekey)'''
        # Included in git sources test/captures/wpa-eap-tls.pcap.gz
        capture_file = os.path.join(config.capture_dir, 'wpa-eap-tls.pcap.gz')
        self.runProcess((config.cmd_tshark,
                '-o', 'wlan.enable_decryption: TRUE',
                '-r', capture_file,
                '-Y', 'wlan.analysis.tk==7d9987daf5876249b6c773bf454a0da7',
                ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('Group Message'))

    def test_80211_wpa_eapol_incomplete_rekeys(self):
        '''WPA decode with message1+2 only and secure bit set on message 2'''
        # Included in git sources test/captures/wpa-test-decode.pcap.gz
        capture_file = os.path.join(config.capture_dir, 'wpa-test-decode.pcap.gz')
        self.runProcess((config.cmd_tshark,
                '-o', 'wlan.enable_decryption: TRUE',
                '-r', capture_file,
                '-Y', 'icmp.resp_to == 4263',
                ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('Echo'))

    def test_80211_wpa_psk_mfp(self):
        '''WPA decode management frames with MFP enabled (802.11w)'''
        # Included in git sources test/captures/wpa-test-decode-mgmt.pcap.gz
        capture_file = os.path.join(config.capture_dir, 'wpa-test-decode-mgmt.pcap.gz')
        self.runProcess((config.cmd_tshark,
                '-o', 'wlan.enable_decryption: TRUE',
                '-r', capture_file,
                '-Y', 'wlan.fixed.reason_code == 2 || wlan.fixed.category_code == 3',
                ),
            env=config.test_env)
        self.assertEqual(self.countOutput('802.11.*SN=.*FN=.*Flags='), 3)


    def test_80211_wpa_tdls(self):
        '''WPA decode traffic in a TDLS (Tunneled Direct-Link Setup) session (802.11z)'''
        if not config.have_libgcrypt16:
            self.skipTest('Requires GCrypt 1.6 or later.')
        # Included in git sources test/captures/wpa-test-decode-tdls.pcap.gz
        capture_file = os.path.join(config.capture_dir, 'wpa-test-decode-tdls.pcap.gz')
        self.runProcess((config.cmd_tshark,
                #'-ouat:80211_keys:"wpa-pwd","12345678"',
                '-o', 'wlan.enable_decryption: TRUE',
                '-r', capture_file,
                '-Y', 'icmp',
                ),
            env=config.test_env)
        self.assertEqual(self.countOutput('ICMP.*Echo .ping'), 2)

class case_decrypt_dtls(subprocesstest.SubprocessTestCase):
    def test_dtls(self):
        '''DTLS'''
        # https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=view&target=snakeoil.tgz
        capture_file = os.path.join(config.capture_dir, 'snakeoil-dtls.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'data.data',
                '-Y', 'data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('69:74:20:77:6f:72:6b:20:21:0a'))

    def test_dtls_psk_aes128ccm8(self):
        '''DTLS 1.2 with PSK, AES-128-CCM-8'''
        capture_file = os.path.join(config.capture_dir, 'dtls12-aes128ccm8.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'dtls.psk:ca19e028a8a372ad2d325f950fcaceed',
                '-x'
            ),
            env=config.test_env)
        dt_count = self.countOutput('Decrypted DTLS')
        wfm_count = self.countOutput('Works for me!.')
        self.assertTrue(dt_count == 7 and wfm_count == 2)

    def test_dtls_udt(self):
        '''UDT over DTLS 1.2 with RSA key'''
        capture_file = os.path.join(config.capture_dir, 'udt-dtls.pcapng.gz')
        key_file = os.path.join(config.key_dir, 'udt-dtls.key')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'dtls.keys_list:0.0.0.0,0,data,{}'.format(key_file),
                '-Y', 'dtls && udt.type==ack',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('UDT'))

class case_decrypt_tls(subprocesstest.SubprocessTestCase):
    def test_ssl(self):
        '''SSL using the server's private key'''
        # https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=view&target=snakeoil2_070531.tgz
        capture_file = os.path.join(config.capture_dir, 'rsasnakeoil2.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'http.request.uri',
                '-Y', 'http',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('favicon.ico'))

    def test_ssl_rsa_pq(self):
        '''SSL using the server's private key with p < q
        (test whether libgcrypt is correctly called)'''
        capture_file = os.path.join(config.capture_dir, 'rsa-p-lt-q.pcap')
        key_file = os.path.join(config.key_dir, 'rsa-p-lt-q.key')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.keys_list:0.0.0.0,443,http,{}'.format(key_file),
                '-Tfields',
                '-e', 'http.request.uri',
                '-Y', 'http',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('/'))

    def test_ssl_with_password(self):
        '''SSL using the server's private key with password'''
        capture_file = os.path.join(config.capture_dir, 'dmgr.pcapng')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'http.request.uri',
                '-Y', 'http',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('unsecureLogon.jsp'))

    def test_ssl_master_secret(self):
        '''SSL using the master secret'''
        capture_file = os.path.join(config.capture_dir, 'dhe1.pcapng.gz')
        key_file = os.path.join(config.key_dir, 'dhe1_keylog.dat')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.keylog_file: {}'.format(key_file),
                '-o', 'ssl.desegment_ssl_application_data: FALSE',
                '-o', 'http.ssl.port: 443',
                '-Tfields',
                '-e', 'http.request.uri',
                '-Y', 'http',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('test'))

    def test_tls12_renegotiation(self):
        '''TLS 1.2 with renegotiation'''
        capture_file = os.path.join(config.capture_dir, 'tls-renegotiation.pcap')
        key_file = os.path.join(config.key_dir, 'rsasnakeoil2.key')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.keys_list:0.0.0.0,4433,http,{}'.format(key_file),
                '-Tfields',
                '-e', 'http.content_length',
                '-Y', 'http',
            ),
            env=config.test_env)
        count_0 = self.countOutput('^0$')
        count_2151 = self.countOutput('^2151$')
        self.assertTrue(count_0 == 1 and count_2151 == 1)

    def test_tls12_psk_aes128ccm(self):
        '''TLS 1.2 with PSK, AES-128-CCM'''
        capture_file = os.path.join(config.capture_dir, 'tls12-aes128ccm.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.psk:ca19e028a8a372ad2d325f950fcaceed',
                '-q',
                '-z', 'follow,ssl,ascii,0',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('http://www.gnu.org/software/gnutls'))

    def test_tls12_psk_aes256gcm(self):
        '''TLS 1.2 with PSK, AES-256-GCM'''
        capture_file = os.path.join(config.capture_dir, 'tls12-aes256gcm.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.psk:ca19e028a8a372ad2d325f950fcaceed',
                '-q',
                '-z', 'follow,ssl,ascii,0',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('http://www.gnu.org/software/gnutls'))

    def test_tls12_chacha20poly1305(self):
        '''TLS 1.2 with ChaCha20-Poly1305'''
        if not config.have_libgcrypt17:
            self.skipTest('Requires GCrypt 1.7 or later.')
        capture_file = os.path.join(config.capture_dir, 'tls12-chacha20poly1305.pcap')
        key_file = os.path.join(config.key_dir, 'tls12-chacha20poly1305.keys')
        ciphers=[
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'ECDHE-RSA-CHACHA20-POLY1305',
            'DHE-RSA-CHACHA20-POLY1305',
            'RSA-PSK-CHACHA20-POLY1305',
            'DHE-PSK-CHACHA20-POLY1305',
            'ECDHE-PSK-CHACHA20-POLY1305',
            'PSK-CHACHA20-POLY1305',
        ]
        stream = 0
        for cipher in ciphers:
            self.runProcess((config.cmd_tshark,
                    '-r', capture_file,
                    '-o', 'ssl.keylog_file: {}'.format(key_file),
                    '-q',
                    '-z', 'follow,ssl,ascii,{}'.format(stream),
                ),
                env=config.test_env)
            stream += 1
            self.assertTrue(self.grepOutput('Cipher is {}'.format(cipher)))

    def test_tls13_chacha20poly1305(self):
        '''TLS 1.3 with ChaCha20-Poly1305'''
        if not config.have_libgcrypt17:
            self.skipTest('Requires GCrypt 1.7 or later.')
        capture_file = os.path.join(config.capture_dir, 'tls13-20-chacha20poly1305.pcap')
        key_file = os.path.join(config.key_dir, 'tls13-20-chacha20poly1305.keys')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'ssl.keylog_file: {}'.format(key_file),
                '-q',
                '-z', 'follow,ssl,ascii,0',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('TLS13-CHACHA20-POLY1305-SHA256'))

class case_decrypt_zigbee(subprocesstest.SubprocessTestCase):
    def test_zigbee(self):
        '''ZigBee'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=7022
        capture_file = os.path.join(config.capture_dir, 'sample_control4_2012-03-24.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'data.data',
                '-Y', 'zbee_aps',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('30:67:63:63:38:65:20:63:34:2e:64:6d:2e:74:76:20'))

class case_decrypt_ansi_c1222(subprocesstest.SubprocessTestCase):
    def test_ansi_c1222(self):
        '''ANSI C12.22'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=9196
        capture_file = os.path.join(config.capture_dir, 'c1222_std_example8.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'c1222.decrypt: TRUE',
                '-o', 'c1222.baseoid: 2.16.124.113620.1.22.0',
                '-Tfields',
                '-e', 'c1222.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('00:10:4d:41:4e:55:46:41:43:54:55:52:45:52:20:53:4e:20:92'))

class case_decrypt_dvb_ci(subprocesstest.SubprocessTestCase):
    def test_dvb_ci(self):
        '''DVB-CI'''
        # simplified version of the sample capture in
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=6700
        capture_file = os.path.join(config.capture_dir, 'dvb-ci_UV1_0000.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'dvb-ci.sek: 00000000000000000000000000000000',
                '-o', 'dvb-ci.siv: 00000000000000000000000000000000',
                '-Tfields',
                '-e', 'dvb-ci.cc.sac.padding',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('80:00:00:00:00:00:00:00:00:00:00:00'))

class case_decrypt_ipsec(subprocesstest.SubprocessTestCase):
    def test_ipsec_esp(self):
        '''IPsec ESP'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12671
        capture_file = os.path.join(config.capture_dir, 'esp-bug-12671.pcapng.gz')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'esp.enable_encryption_decode: TRUE',
                '-Tfields',
                '-e', 'data.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('08:09:0a:0b:0c:0d:0e:0f:10:11:12:13:14:15:16:17'))

class case_decrypt_ike_isakmp(subprocesstest.SubprocessTestCase):
    def test_ikev1_certs(self):
        '''IKEv1 (ISAKMP) with certificates'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=7951
        capture_file = os.path.join(config.capture_dir, 'ikev1-certs.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'x509sat.printableString',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('OpenSwan'))

    def test_ikev1_simultaneous(self):
        '''IKEv1 (ISAKMP) simultaneous exchanges'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12610
        capture_file = os.path.join(config.capture_dir, 'ikev1-bug-12610.pcapng.gz')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.hash',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('b5:25:21:f7:74:96:74:02:c9:f6:ce:e9:5f:d1:7e:5b'))

    def test_ikev1_unencrypted(self):
        '''IKEv1 (ISAKMP) unencrypted phase 1'''
        # https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12620
        capture_file = os.path.join(config.capture_dir, 'ikev1-bug-12620.pcapng.gz')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.hash',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('40:04:3b:64:0f:43:73:25:0d:5a:c3:a1:fb:63:15:3c'))

    def test_ikev2_3des_sha160(self):
        '''IKEv2 decryption test (3DES-CBC/SHA1_160)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-3des-sha1_160.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('02:f7:a0:d5:f1:fd:c8:ea:81:03:98:18:c6:5b:b9:bd:09:af:9b:89:17:31:9b:88:7f:f9:ba:30:46:c3:44:c7'))

    def test_ikev2_aes128_ccm12(self):
        '''IKEv2 decryption test (AES-128-CCM-12) - with CBC-MAC verification'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes128ccm12.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('c2:10:43:94:29:9e:1f:fe:79:08:ea:72:0a:d5:d1:37:17:a0:d4:54:e4:fa:0a:21:28:ea:68:94:11:f4:79:c4'))

    def test_ikev2_aes128_ccm12_2(self):
        '''IKEv2 decryption test (AES-128-CCM-12 using CTR mode, without checksum)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes128ccm12-2.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('aa:a2:81:c8:7b:4a:19:04:6c:57:27:1d:55:74:88:ca:41:3b:57:22:8c:b9:51:f5:fa:96:40:99:2a:02:85:b9'))

    def test_ikev2_aes192ctr_sha512(self):
        '''IKEv2 decryption test (AES-192-CTR/SHA2-512)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes192ctr.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('3e:c2:3d:cf:93:48:48:56:38:40:7c:75:45:47:ae:b3:08:52:90:08:2c:49:f5:83:fd:ba:e5:92:63:a2:0b:4a'))

    def test_ikev2_aes256cbc_sha256(self):
        '''IKEv2 decryption test (AES-256-CBC/SHA2-256)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes256cbc.pcapng')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('e1:a8:d5:50:06:42:01:a7:ec:02:4a:85:75:8d:06:73:c6:1c:5c:51:0a:c1:3b:cd:22:5d:63:27:f5:0d:a3:d3'))

    def test_ikev2_aes256ccm16(self):
        '''IKEv2 decryption test (AES-256-CCM-16)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes256ccm16.pcapng')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('fa:2e:74:bd:c0:1e:30:fb:0b:3d:dc:97:23:c9:44:90:95:96:9d:a5:1f:69:e5:60:20:9d:2c:2b:79:40:21:0a'))

    def test_ikev2_aes256gcm16(self):
        '''IKEv2 decryption test (AES-256-GCM-16)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes256gcm16.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('9a:b7:1f:14:ab:55:3c:ad:87:3a:1a:a7:0b:99:df:15:5d:ee:77:cd:cf:36:94:b3:b7:52:7a:cb:b9:71:2d:ed'))

    def test_ikev2_aes256gcm8(self):
        '''IKEv2 decryption test (AES-256-GCM-8)'''
        capture_file = os.path.join(config.capture_dir, 'ikev2-decrypt-aes256gcm8.pcap')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'isakmp.auth.data',
            ),
            env=config.test_env)
        self.assertTrue(self.grepOutput('4a:66:d8:22:d0:af:bc:22:ad:9a:92:a2:cf:42:87:c9:20:ad:8a:c3:b0:69:a4:a7:e7:5f:e0:a5:d4:99:f9:14'))

class case_decrypt_http2(subprocesstest.SubprocessTestCase):
    def test_http2(self):
        '''HTTP2 (HPACK)'''
        if not config.have_nghttp2:
            self.skipTest('Requires nghttp2.')
        capture_file = os.path.join(config.capture_dir, 'packet-h2-14_headers.pcapng')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-Tfields',
                '-e', 'http2.header.value',
                '-d', 'tcp.port==3000,http2',
            ),
            env=config.test_env)
        test_passed = self.grepOutput('nghttp2')
        if not test_passed:
            self.log_fd.write(u'\n\n-- Verbose output --\n\n')
            self.runProcess((config.cmd_tshark,
                    '-r', capture_file,
                    '-V',
                    '-d', 'tcp.port==3000,http2',
                ),
                env=config.test_env)
        self.assertTrue(test_passed)

class case_decrypt_kerberos(subprocesstest.SubprocessTestCase):
    def test_kerberos(self):
        '''Kerberos'''
        # Files are from krb-816.zip on the SampleCaptures page.
        if not config.have_kerberos:
            self.skipTest('Requires nghttp2.')
        capture_file = os.path.join(config.capture_dir, 'krb-816.pcap.gz')
        keytab_file = os.path.join(config.key_dir, 'krb-816.keytab')
        self.runProcess((config.cmd_tshark,
                '-r', capture_file,
                '-o', 'kerberos.decrypt: TRUE',
                '-o', 'kerberos.file: {}'.format(keytab_file),
                '-Tfields',
                '-e', 'kerberos.keyvalue',
            ),
            env=config.test_env)
        # keyvalue: ccda7d48219f73c3b28311c4ba7242b3
        self.assertTrue(self.grepOutput('cc:da:7d:48:21:9f:73:c3:b2:83:11:c4:ba:72:42:b3'))
