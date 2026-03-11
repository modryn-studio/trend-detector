Delivered-To: luke@modrynstudio.com
Received: by 2002:a05:6214:1cc5:b0:89a:632c:5e42 with SMTP id g5csp36825qvd;
        Wed, 11 Mar 2026 11:07:33 -0700 (PDT)
X-Received: by 2002:a05:6808:1907:b0:467:14c7:a8ae with SMTP id 5614622812f47-46733439e2amr1906352b6e.21.1773252452437;
        Wed, 11 Mar 2026 11:07:32 -0700 (PDT)
ARC-Seal: i=1; a=rsa-sha256; t=1773252452; cv=none;
        d=google.com; s=arc-20240605;
        b=NMVphwgKohtBgwnWNagMmuwhsuKI+LWK0fcRR2g/IQOgLJmCLTdoN5w844UNdwv4XU
         ejhDi/2m5x8k5aADLkrh2RJ/MR4WeU1M85Vbida4z6EcItkI/IGte7XoVnqC7ulTT3IO
         YrubAGEhLloPhcLNsBNJmfFKF+sQQLHKYB2SmJ09UzuRzgKpN9UzL5crCKLHlh+zDNXu
         /cAviWbznloCM3h58VHf75G6LwS0S8WQZgYUPI14mrdOEWZgK+51yHrRa0GuDOZji4KF
         h7Apxr5IAeqd1XF+Zl2pRcvF5r054p/R7TpBLJ2iSiUaxbdidvKtyT9bSYvzCjBUDZDJ
         EWCw==
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20240605;
        h=to:from:subject:message-id:gmsai:list-id:feedback-id:precedence
         :list-unsubscribe:list-unsubscribe-post:reply-to:date:mime-version
         :dkim-signature;
        bh=Hy1gXam9A9Htc1NvbyT7cPAKP2FHdmB9esY262q4PRU=;
        fh=pjEuWj6yadAKaZ6JANyCOUOzkUoS3IuUZFxyQLfRFQo=;
        b=GMlluKv/pM3H6MCXMTM6Kle8U148VuNWkBws4/I2RhI5kJk98vMGLmfZKcKwpZHwOV
         fsuwGAn/39rPYmG3c/+AmY4nBe0OIZQ/fG3FQptNX8yJhuRjQm2Gssl9En2vCZECRsnG
         Ig28NGny2ss1jqTOzsGv57qcJ4XLEJuTx4X1bUGvoOhRyVQJfQ6b3Pvf+KyOpD7bR0RJ
         K4rsM2FdhVe3ho+5/b1+XHzWBAQkJPbuXSzJKwm4RZobYQkUdpBYiceYeDAVPdbEdFjX
         YO/Lm6GAIJVUIXOBYsgCnY+UYdccItDkBhVMNVfmXwtAb+7BwBU6FSZqlJUnqIgOp0TI
         /C8w==;
        dara=google.com
ARC-Authentication-Results: i=1; mx.google.com;
       dkim=pass header.i=@google.com header.s=20230601 header.b=clJ8qo0+;
       spf=pass (google.com: domain of 3zk-xaq4kbn0sqdmcr-mnqdokxfnnfkd.bnlktjdlncqxmrstchn.bnl@scoutcamp.bounces.google.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=3ZK-xaQ4KBN0SQDMCR-MNQDOKXFNNFKD.BNLKTJDLNCQXMRSTCHN.BNL@scoutcamp.bounces.google.com;
       dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=google.com;
       dara=neutral header.i=@modrynstudio.com
Return-Path: <3ZK-xaQ4KBN0SQDMCR-MNQDOKXFNNFKD.BNLKTJDLNCQXMRSTCHN.BNL@scoutcamp.bounces.google.com>
Received: from mail-sor-f69.google.com (mail-sor-f69.google.com. [209.85.220.69])
        by mx.google.com with SMTPS id 5614622812f47-46734196166sor867812b6e.6.2026.03.11.11.07.32
        for <luke@modrynstudio.com>
        (Google Transport Security);
        Wed, 11 Mar 2026 11:07:32 -0700 (PDT)
Received-SPF: pass (google.com: domain of 3zk-xaq4kbn0sqdmcr-mnqdokxfnnfkd.bnlktjdlncqxmrstchn.bnl@scoutcamp.bounces.google.com designates 209.85.220.69 as permitted sender) client-ip=209.85.220.69;
Authentication-Results: mx.google.com;
       dkim=pass header.i=@google.com header.s=20230601 header.b=clJ8qo0+;
       spf=pass (google.com: domain of 3zk-xaq4kbn0sqdmcr-mnqdokxfnnfkd.bnlktjdlncqxmrstchn.bnl@scoutcamp.bounces.google.com designates 209.85.220.69 as permitted sender) smtp.mailfrom=3ZK-xaQ4KBN0SQDMCR-MNQDOKXFNNFKD.BNLKTJDLNCQXMRSTCHN.BNL@scoutcamp.bounces.google.com;
       dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=google.com;
       dara=neutral header.i=@modrynstudio.com
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=google.com; s=20230601; t=1773252452; x=1773857252; darn=modrynstudio.com;
        h=to:from:subject:message-id:gmsai:list-id:feedback-id:precedence
         :list-unsubscribe:list-unsubscribe-post:reply-to:date:mime-version
         :from:to:cc:subject:date:message-id:reply-to;
        bh=Hy1gXam9A9Htc1NvbyT7cPAKP2FHdmB9esY262q4PRU=;
        b=clJ8qo0+U3yNdNitr1J/3KrYUlCxkh/FBP6JiqJjEoe6+GbYjGDw9SWi+TV8L7az+l
         Q4Xu+BL/MXyX6/ZyDAG3qmjK3BbM0Sc8DpfMgmyf52DamKzltqSVG6MdgQlQrkMCmdmI
         G28VOm/R8gkvtSJmxl8hq58w7yncRsilokB3/0KYrIwYa13Xvz3Uycvq9oKUPtI3SahS
         IPQbpW5CNRDzr0KbRZgJMBUduaQBvudpA5Uk6UWUeRohdwLC7LymkmA30OH3z6ETGzaC
         aDtsWaKF/gWZ3hE7LwCus9q9IrEQAgs8ncNep6PgrPx5fghLv3ygshkUSuwAhIhk8tuF
         yFZw==
X-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=1e100.net; s=20230601; t=1773252452; x=1773857252;
        h=to:from:subject:message-id:gmsai:list-id:feedback-id:precedence
         :list-unsubscribe:list-unsubscribe-post:reply-to:date:mime-version
         :x-gm-message-state:from:to:cc:subject:date:message-id:reply-to;
        bh=Hy1gXam9A9Htc1NvbyT7cPAKP2FHdmB9esY262q4PRU=;
        b=uaVLbFvb/qnUmknxHviqP+87phatdCQc9JNyRjKXQumsbsxCNO+Guom9C8VHxXMooG
         oX49f55G8HUQdJcFXr8/6a/91/HtDbUGdtgfVpqwsw7jdWcfmTHEGgSY4uXGSpJmW0I6
         +S1mCQAszuu0iNfdlTloI2bk+9PXiX/vp2A8VaS9VkgentP4g/P8+oiJL64jxpaBGpnB
         tM93r11w1RB24O5vO7WNyKbJl30WwucPSOklZZD5cjfpXwAuSkxNGPjhtrKrpsNjWEHv
         m6/o4UZ8xIkeEa8lEcpPV6Fyi3tkc/aG4aKGj0/pDvOswt8ZMf26jIixU41E0TBu/yFt
         Jc4w==
X-Gm-Message-State: AOJu0YwFUNYsUupp03C9gOwWm/Hzfw3ZoI/KrY2P0tDENLMSnXiISyiQ kgRKdfdXt7xm0qXVACDnbReLAQ47RiXjbXACqpMKoanBMQkdwUI=
MIME-Version: 1.0
X-Received: by 2002:a05:6820:1b06:b0:67b:ad63:95c7 with SMTP id 006d021491bc7-67bc89a763amr2029545eaf.36.1773252452211; Wed, 11 Mar 2026 11:07:32 -0700 (PDT)
Date: Wed, 11 Mar 2026 11:07:32 -0700
Reply-To: Google Trends <trends-noreply@google.com>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
List-Unsubscribe: <https://myaccount.google.com/communication-preferences/auto/unsubscribe/gt/AEJ26qvFQDVfgZ9x8sgcrfxgxh-cvFd46zXhdGbiEJvjbDRXneH3m_bnEulR9GPTGR6zVW1eRRZ0WZjJE1cuhUvxj1hJvcaVsUGEVp_e9pX7E0UmjDHXnrFLDFdDjOJSI_AfgEUQ4QYCzx2rsEypBq0vXW8BeMSc_ZAsU7DwdbE2WWYWoLBPctACzJxfKlqHcpYNIwxa2uOPXJk3iY3VAz1vJUU18QsRR4BrWKiq6j1DwDYeLiZVdg?utm_source=gm_header&utm_medium=email>
Precedence: bulk
Feedback-ID: P-455174802--930586666:C20237020:M111129704-en-US:gamma
List-Id: <5bc428ec6d649002d87571488932eacf5aa4ca54.google.com>
gmsai: false
X-Google-Notification-Metadata: EgA
X-Notifications: 434297e170360000
X-Notifications-Bounce-Info: AeDslag83jvYkQDAd3R-_yOxvSc548EwNiJZC6bb2LAu5zoaq8adeuE35gpuCwYXwbB2PoQc-Alidq8bS5dUV5MMDovpByAeCamIgISr0b6Ue-cdP-4jMMm35-cex7Z6Q_bVQI6c19o0dXrrOm-wy8An7HIF2kvseD2N2Udz1w1KLY_bilz-tsilXMNcV-KcgsSQzCNgXDzn5UzSdhzJgqLZJLUFa5H3k5KDuIRdk3NMD4lAyEO74oTtgVMSMBRMw3Psij_WrvVQ0RSZYUL9esJorEsARNdgoATFChzvGjecyH1lkAlFyzP2O2_FxH4g79ea7udd09IrCnz1ZQ5uepyJu_lQ6HBvxhgKJf2xRhZUIwUWjwYBxAD9t9EUIhgvScP0TjdNnMrjX2TbTRrzoN72LrQjmbe08xfnB52FA21gfD-Bbq_W5j6oDRog4_bgQzRHZBGxr-u38Jr6TI4_1_zgm9B4cu3bmFb_o2yNg92KXxqz0L-XtpMDit0AO6PUHwQ_fdvbm__is1FpyrYSia_pN-HsdWIZvF0DHrvO3oNqDzPe-8Px51WwT83-NjAwNjA0MDQxNTM1NTk2OTMzMg
Message-ID: <79da5ae4917154cc357eed204c266caf40c3acc5-20237020-111821077@google.com>
Subject: Ube • Pi Day • St. Patrick’s Day
From: Google Trends <trends-noreply@google.com>
To: luke@modrynstudio.com
Content-Type: multipart/alternative; boundary="00000000000082e44e064cc3829c"

--00000000000082e44e064cc3829c
Content-Type: text/plain; charset="UTF-8"; format=flowed; delsp=yes
Content-Transfer-Encoding: base64

aW1hZ2UucG5nDQoNCg0KDQpVYmUg4oCiIFBpIERheSDigKIgU3QuIFBhdHJpY2sncyBEYXkNCg0K
TWFyY2ggMTEsIDIwMjYNCg0KDQoNCg0KSmVubnkgTGVlLCBMZWFkIERhdGEgQW5hbHlzdA0KDQp3
aXRoIFNhYnJpbmEgRWxmYXJyYSBhbmQgS2F0aWUgU2VhdG9uDQoNCg0KVG9wIFRyZW5kcw0KDQoN
Cg0K4oCceG8ga2l0dHkgdHJhaWxlcuKAnSBpbmNyZWFzZWQgKzc1MCUgb3ZlciB0aGUgcGFzdCB3
ZWVrIGFuZCB0aGUgdG9wIHRyZW5kaW5nICANCuKAnHdpbGwga2l0dHnigKbigJ0gd2FzIOKAnHdp
bGwga2l0dHkgZW5kIHVwIHdpdGggbWluaG/igJ0NCg0KDQpPdmVyIHRoZSBwYXN0IHdlZWssIHRo
ZSB0b3AgdHJlbmRpbmcg4oCcdHJlbmTigJ0gd2FzIOKAnHdoYXQgd2VyZSB5b3UgbGlrZSBpbiB0
aGUgIA0KOTBz4oCdIHdoaWNoIHNwaWtlZCArMSw5ODUlLiDigJxQZWRybyBwYXNjYWwgaW4gdGhl
IDkwc+KAnSBpcyB0aGUgdG9wIHRyZW5kaW5nICANCmNlbGVicml0eSDigJwuLi5pbiB0aGUgOTBz
4oCdDQoNCg0KRW5oeXBlbiBpcyB0aGUgdG9wIHRyZW5kaW5nIGVudGVydGFpbm1lbnQgc2VhcmNo
IG92ZXIgdGhlIHBhc3QgZGF5IHdpdGggIA0K4oCcd2h5IGlzIGhlZXNldW5nIGxlYXZpbmfigJ0g
YmVpbmcgYSBicmVha291dCBzZWFyY2ggYW5kIEhlZXNldW5nIGlzIHRoZSB0b3AgIA0KdHJlbmRp
bmcg4oCcc29sbyBhbGJ1beKAnQ0KDQoNCuKAnGphcGFuZXNlIHN3ZWV0IHBvdGF0b+KAnSBpcyBh
dCBhbiBhbGwtdGltZSBoaWdoIGZvciB0aGUgc2Vjb25kIHRpbWUgaW4gMjAyNi4gIA0K4oCcamFw
YW5lc2Ugc3dlZXQgcG90YXRvIGNob2NvbGF0ZSBjYWtl4oCdIGlzIHRoZSB0b3AgdHJlbmRpbmcg
cmVsYXRlZCByZWNpcGUgIA0Kb3ZlciB0aGUgcGFzdCBtb250aA0KDQoNCkRlc2lnbmVyIE5hcmNp
c28gUm9kcmlndWV6IGlzIGJlaW5nIHNlYXJjaGVkIG1vcmUgdGhhbiBldmVyIGJlZm9yZS4g4oCc
c2xpcCAgDQp3ZWRkaW5nIGRyZXNzZXPigJ0gc3Bpa2VkICszNzUlIGFuZCDigJxjYmsgd2VkZGlu
ZyBkcmVzc+KAnSB3YXMgYSBicmVha291dCBzZWFyY2ggIA0Kb3ZlciB0aGUgcGFzdCB3ZWVrDQoN
Cg0KDQpHb29nbGUgVHJlbmRzIFN0b3J5IFBhZ2UNCg0KVGhlIDk4dGggQWNhZGVteSBBd2FyZHMg
d2lsbCB0YWtlIHBsYWNlIG9uIFN1bmRheSwgTWFyY2ggMTUsIDIwMjYNCg0KaW1hZ2UuanBlZw0K
DQoNClViZQ0KDQoNCg0KU2VhcmNoIGludGVyZXN0IGluIHB1cnBsZSB5YW0gb3Ig4oCcdWJl4oCd
IGFyZSBjdXJyZW50bHkgYXQgYW4gYWxsLXRpbWUgaGlnaCBpbiAgDQp0aGUgVVMgd2l0aCDigJx3
aGF0IGRvZXMgdWJlIHRhc3RlIGxpa2XigJ0gbW9yZSB0aGFuIGRvdWJsaW5nIG92ZXIgdGhlIHBh
c3Qgd2Vlaw0KDQoNCuKAnHdoYXQgaXMgdWJl4oCdIGlzIGFsc28gYmVpbmcgc2VhcmNoZWQgbW9y
ZSB0aGFuIGV2ZXIgYW5kIOKAnGlzIHViZSBhbmQgdGFybyAgDQp0aGUgc2FtZeKAnSBpcyBvbmUg
b2YgdGhlIHRvcCBxdWVzdGlvbnMgc2VhcmNoZWQgYWJvdXQgdWJlIG9mIGFsbCB0aW1lDQoNCg0K
4oCcd2hhdCBpcyB1YmUgY29sZCBmb2Ft4oCdIHdhcyB0aGUgdG9wLXRyZW5kaW5nIHF1ZXN0aW9u
IG9uIOKAnGNvbGQgZm9hbeKAnSBpbiB0aGUgIA0KcGFzdCBtb250aC4g4oCcVWJlIHdpdGggY29m
ZmVl4oCdIGFuZCDigJx1YmUgd2l0aCBjaGVlc2XigJ0gd2VyZSB0aGUgdG9wIHR3byAgDQp0cmVu
ZGluZyDigJx1YmUgd2l0aOKApuKAnSBzZWFyY2hlcyBpbiB0aGUgcGFzdCBtb250aA0KDQoNClVi
ZSBUcmVzIExlY2hlcyByb3NlICs1MDAlIGluIHRoZSBwYXN0IG1vbnRoLCBhbmQg4oCcaG93IHRv
IG1ha2UgdWJlIGV4dHJhY3QgIA0KZnJvbSBzY3JhdGNo4oCdIHdhcyB0aGUgdG9wLXRyZW5kaW5n
IOKAnGhvdyB0byBtYWtlIHViZeKApuKAnQ0KDQoNCg0KUGkoZSkgRGF5DQoNCg0KDQpPdmVyIHRo
ZSBwYXN0IG1vbnRoLCDigJxhcmVhIG9mIGEgY2lyY2xl4oCdIGlzIHRoZSB0b3AgZm9ybXVsYSBz
ZWFyY2hlZCB3aXRoICANCnBpLCBmb2xsb3dlZCBieSDigJxjaXJjdW1mZXJlbmNlIG9mIGEgY2ly
Y2xl4oCdDQoNCg0K4oCcbWVtb3JpemUgcGnigJ0gc3Bpa2VzIGV2ZXJ5IE1hcmNoLCBhbmQg4oCc
aG93IHRvIG1lbW9yaXplIHBpIGZhc3TigJ0gd2FzIG9uZSBvZiAgDQp0aGUgdG9wLXRyZW5kaW5n
IOKAnGhvdyB0byBtZW1vcml6ZeKApuKAnSBzZWFyY2hlcyBpbiB0aGUgcGFzdCBtb250aA0KDQoN
CuKAnGxlbnRpbCB2ZWdldGFibGUgcGllIHJlY2lwZeKAnSB3YXMgdGhlIHRvcC10cmVuZGluZyDi
gJxwaWUgcmVjaXBl4oCdIHNlYXJjaGVkIGluICANCnRoZSBwYXN0IHdlZWssIGZvbGxvd2VkIGJ5
IOKAnGF1dGhlbnRpYyBzaGVwaGVyZCdzIHBpZSByZWNpcGXigJ0NCg0KDQoNClN0LiBQYXRyaWNr
J3MgRGF5DQoNCg0KDQrigJxzaGFtcm9jayBzaGFrZeKAnSB3YXMgdGhlIHRvcCB0cmVuZGluZyDi
gJxob3cgdG8gbWFrZeKApnNoYWtl4oCdLiBUaGUgdG9wIHRyZW5kaW5nICANCnF1ZXN0aW9uIGFi
b3V0IHRoZSBzaGFtcm9jayBzaGFrZSBpcyDigJx3aGF0IGlzIGEgc2hhbXJvY2sgc2hha2UgZmxh
dm9y4oCdIGFuZCAgDQrigJx3aGF0IGRvZXMgc2hhbXJvY2sgc2hha2UgdGFzdGUgbGlrZeKAnQ0K
DQoNClNlYXJjaCBpbnRlcmVzdCBpbiDigJx3aGF0IGlzIHNhbHQgYmVlZuKAnSBoaXQgYW4gYWxs
LXRpbWUgaGlnaCB0aGlzIHllYXIsIGFuZCAgDQrigJxjb3JuZWQgYmVlZiB0YWNvc+KAnSBzcGlr
ZWQgKzE4MCUgaW4gdGhlIHBhc3QgbW9udGgNCg0KDQpTZWFyY2ggaW50ZXJlc3QgaW4g4oCcbGVw
cmVjaGF1biBiZWFyZCBmb3IgYW1pZ3VydW1p4oCdIHdhcyB0aGUgdG9wLXRyZW5kaW5nICANCuKA
nGxlcHJlY2hhdW4gYmVhcmQgZm9y4oCm4oCdIHNlYXJjaGVkIGluIHRoZSBwYXN0IG1vbnRoLCBh
bmQg4oCcbGVwcmVjaGF1biBiZWFyZCAgDQptb2xk4oCdIGJyb2tlIG91dCBpbiBzZWFyY2gNCg0K
DQrigJxyYWluYm93IGNoYWlu4oCdIGlzIGF0IGEgMTAteWVhciBoaWdoLCBhbmQg4oCccGFwZXIg
Y2hhaW4gcmFpbmJvd+KAnSBzcGlrZWQgIA0KKzE3MCUgaW4gdGhlIHBhc3QgbW9udGgNCg0KDQri
gJxwb3Qgb2YgZ29sZOKAnSB3YXMgc2VhcmNoZWQgb3ZlciAyeCBtb3JlIHRoYW4g4oCcbGVwcmVj
aGF1biB0cmFw4oCdIGluIHRoZSBwYXN0ICANCnRocmVlIG1vbnRocywgYW5kIOKAnHBvdCBvZiBn
b2xkIGNvbG9yaW5nIHBhZ2XigJ0gd2FzIHRoZSBzZWNvbmQtbW9zdCB0cmVuZGluZyAgDQrigJxj
b2xvcmluZyBwYWdl4oCdIHNlYXJjaGVkIGluIHRoZSBwYXN0IHdlZWsNCg0KDQoNCmltYWdlLnBu
Zw0KDQoNCg0KTWFyayBZb3VyIENhbGVuZGFycw0KDQoNCg0KRWlkIEFsIEZpdHINCg0KTWFyY2gg
MjAsIDIwMjYNCg0KU3ByaW5nIEVxdWlub3gNCk1hcmNoIDIwLCAyMDI2DQoNCk1hc3RlcnMgVG91
cm5hbWVudA0KQXByaWwgNiwgMjAyNg0KDQoNCg0KKzM1JSBwYXN0IHdlZWsNCg0KKzE0NSUgcGFz
dCBtb250aA0KDQorMTEwJSBzYW1lIHdlZWsgbGFzdCB5ZWFyDQoNCisxNSUgcGFzdCB3ZWVrDQoN
CisxMDAlIHBhc3QgbW9udGgNCg0KLTElIHNhbWUgd2VlayBsYXN0IHllYXINCg0KKzIwJSBwYXN0
IHdlZWsNCg0KKzMwJSBwYXN0IG1vbnRoDQoNCi0yJSBzYW1lIHdlZWsgbGFzdCB5ZWFyDQoNCg0K
DQoNCk5vdGVzDQoNCg0KDQpVbml0ZWQgU3RhdGVzIGRhdGEgdW5sZXNzIHN0YXRlZCBvdGhlcndp
c2UgYW5kIGlzIGFjY3VyYXRlIGF0IHRoZSB0aW1lIG9mICANCnB1YmxpY2F0aW9uDQoNCg0KQnJl
YWtvdXQ6IHNlYXJjaCB0ZXJtcyBoYWQgYSB0cmVtZW5kb3VzIGluY3JlYXNlLCBpbiBzb21lIGNh
c2VzIGJlY2F1c2UgIA0KdGhlc2UgdGVybXMgYXJlIG5ldyBhbmQgaGFkIGZldyAoaWYgYW55KSBw
cmlvciBzZWFyY2hlcw0KDQoNClRvcCBvciBNb3N0IFNlYXJjaGVkOiBzZWFyY2ggdGVybXMgdGhh
dCByYW5rIGhpZ2hlc3QgYnkgc2VhcmNoIHZvbHVtZSBmb3IgYSAgDQpnaXZlbiB0aW1lZnJhbWUg
YW5kIGxvY2F0aW9uDQoNCg0KVHJlbmRpbmcgU2VhcmNoZXM6IHNlYXJjaCB0ZXJtcyB0aGF0IGhh
ZCB0aGUgaGlnaGVzdCBzcGlrZSBpbiB0cmFmZmljIG92ZXIgIA0KYSBnaXZlbiB0aW1lIHBlcmlv
ZCBhcyBjb21wYXJlZCB3aXRoIHRoZSBwcmV2aW91cyBlcXVpdmFsZW50IHBlcmlvZA0KDQoNCkZv
ciBtb3JlIGluZm9ybWF0aW9uIGFib3V0IG91ciBtZXRob2RvbG9neSBhbmQgaG93IHRvIGludGVy
cHJldCB0aGUgZGF0YSwgIA0KcGxlYXNlIHJlYWQgb3VyIEZBUXMgYW5kIGxlYXJuIG1vcmUgaGVy
ZQ0KDQoNCklmIHlvdSdkIGxpa2UgdG8gdXNlIFRyZW5kcyBkYXRhLCBwbGVhc2UgcmVhZDogSG93
IHRvIHVzZSBhbmQgY2l0ZSBUcmVuZHMgIA0KZGF0YQ0KDQoNCg0KR29vZ2xlIExMQyAxNjAwIEFt
cGhpdGhlYXRyZSBQYXJrd2F5LCBNb3VudGFpbiBWaWV3LCBDQSA5NDA0My4NCg0KVGhpcyBlbWFp
bCB3YXMgc2VudCB0byBsdWtlQG1vZHJ5bnN0dWRpby5jb20gYmVjYXVzZSB5b3UgaGF2ZSBzdWJz
Y3JpYmVkIHRvICANCnRoZSBHb29nbGUgVHJlbmRzIERhaWx5IFRyZW5kaW5nIE5ld3NsZXR0ZXIu
IElmIHlvdSBkbyBub3Qgd2lzaCB0byByZWNlaXZlICANCnN1Y2ggZW1haWxzIGluIHRoZSBmdXR1
cmUsIHBsZWFzZSB1bnN1YnNjcmliZSBoZXJlDQo=
--00000000000082e44e064cc3829c
Content-Type: text/html; charset="UTF-8"
Content-Transfer-Encoding: quoted-printable

<div dir=3Dltr><span id=3Dgmail-docs-internal-guid-4fbdaba1-7fff-9551-d1a0-=
e64d8b7ad6f8><p dir=3Dltr style=3Dline-height:1.38;text-align:justify;margi=
n-top:0pt;margin-bottom:6pt><span style=3Dfont-size:11pt;font-family:Arial,=
sans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-numer=
ic:normal;font-variant-east-asian:normal;font-variant-alternates:normal;ver=
tical-align:baseline><span style=3Dborder:none;display:inline-block;overflo=
w:hidden;width:194px;height:35px><img src=3Dhttps://services.google.com/fh/=
files/misc/google_trends_logo_lockup_horizontal.png alt=3Dimage.png width=
=3D194 height=3D57></span></span><span style=3Dfont-size:11pt;font-family:A=
rial,sans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-=
numeric:normal;font-variant-east-asian:normal;font-variant-alternates:norma=
l;vertical-align:baseline><br><br></span></p><p dir=3Dltr style=3Dline-heig=
ht:1.656;text-align:center;margin-top:0pt;margin-bottom:0pt><span style=3D"=
font-size:16pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0=
,0);background-color:transparent;font-variant-numeric:normal;font-variant-e=
ast-asian:normal;font-variant-alternates:normal;vertical-align:baseline">Ub=
e =E2=80=A2 Pi Day =E2=80=A2 St. Patrick=E2=80=99s Day</span></p><p dir=3Dl=
tr style=3Dline-height:1.38;text-align:center;margin-top:0pt;margin-bottom:=
0pt><span style=3D"font-size:11pt;font-family:&quot;Google Sans&quot;,sans-=
serif;color:rgb(67,67,67);background-color:transparent;font-variant-numeric=
:normal;font-variant-east-asian:normal;font-variant-alternates:normal;verti=
cal-align:baseline">March 11, 2026</span><span style=3Dfont-size:11pt;font-=
family:Arial,sans-serif;color:rgb(0,0,0);background-color:transparent;font-=
variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternat=
es:normal;vertical-align:baseline>=C2=A0</span></p><br><br><br><p dir=3Dltr=
 style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span style=3D"f=
ont-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(67,6=
7,67);background-color:transparent;font-variant-numeric:normal;font-variant=
-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline">=
Jenny Lee, Lead Data Analyst</span></p><p dir=3Dltr style=3Dline-height:1.3=
8;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size:11pt;font-famil=
y:&quot;Google Sans&quot;,sans-serif;color:rgb(67,67,67);background-color:t=
ransparent;font-style:italic;font-variant-numeric:normal;font-variant-east-=
asian:normal;font-variant-alternates:normal;vertical-align:baseline">with S=
abrina Elfarra and Katie Seaton</span></p><p dir=3Dltr style=3Dline-height:=
1.38;margin-top:0pt;margin-bottom:0pt></p><hr><p></p><h3 dir=3Dltr style=3D=
line-height:1.38;margin-top:16pt;margin-bottom:4pt><span style=3D"font-size=
:14pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(66,133,244);=
background-color:transparent;font-weight:400;font-variant-numeric:normal;fo=
nt-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:=
baseline">Top Trends</span></h3><ul style=3Dmargin-top:0px;margin-bottom:0p=
x><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-family:&q=
uot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transpar=
ent;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant=
-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr st=
yle=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentation=
><span style=3Dfont-size:11pt;background-color:transparent;font-variant-num=
eric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;v=
ertical-align:baseline>=E2=80=9C</span><a href=3Dhttps://c.gle/AEJ26qtlbnVR=
Yo8BSnjbj2YDtE_wtNPwz3o8rZCdcI0jicgkj9e8WXWPAurYQusVhbDMFs2SWcpkkl3Lz9P32Xk=
q_L2xaL-b2JlL1xEZI4igDnhZeeEJwCtlBnpCb0KSf7GQJRENDUON76C8tNOvDQWy9_3ujPeNE0=
7TI2CbN5LPiHRTyj94va-xglrNhgomaPHKMg4q style=3Dtext-decoration-line:none><s=
pan style=3Dfont-size:11pt;background-color:transparent;font-variant-numeri=
c:normal;font-variant-east-asian:normal;font-variant-alternates:normal;text=
-decoration-line:underline;vertical-align:baseline>xo kitty trailer</span><=
/a><span style=3Dfont-size:11pt;background-color:transparent;font-variant-n=
umeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal=
;vertical-align:baseline>=E2=80=9D increased +750% over the past week and t=
he top trending =E2=80=9Cwill kitty=E2=80=A6=E2=80=9D was =E2=80=9C</span><=
span style=3Dfont-size:11pt;background-color:transparent;font-weight:700;fo=
nt-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alter=
nates:normal;vertical-align:baseline>will kitty end up with minho</span><sp=
an style=3Dfont-size:11pt;background-color:transparent;font-variant-numeric=
:normal;font-variant-east-asian:normal;font-variant-alternates:normal;verti=
cal-align:baseline>=E2=80=9D=C2=A0</span></p></li><li dir=3Dltr style=3D"li=
st-style-type:disc;font-size:11pt;font-family:&quot;Google Sans&quot;,sans-=
serif;color:rgb(0,0,0);background-color:transparent;font-variant-numeric:no=
rmal;font-variant-east-asian:normal;font-variant-alternates:normal;vertical=
-align:baseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;marg=
in-top:0pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:11=
pt;background-color:transparent;font-variant-numeric:normal;font-variant-ea=
st-asian:normal;font-variant-alternates:normal;vertical-align:baseline>Over=
 the past week, the top trending =E2=80=9Ctrend=E2=80=9D was =E2=80=9C</spa=
n><span style=3Dfont-size:11pt;background-color:transparent;font-weight:700=
;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-al=
ternates:normal;vertical-align:baseline>what were you like in the 90s</span=
><span style=3Dfont-size:11pt;background-color:transparent;font-variant-num=
eric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;v=
ertical-align:baseline>=E2=80=9D which spiked +1,985%. =E2=80=9C</span><spa=
n style=3Dfont-size:11pt;background-color:transparent;font-weight:700;font-=
variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternat=
es:normal;vertical-align:baseline>Pedro pascal in the 90s</span><span style=
=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:normal;=
font-variant-east-asian:normal;font-variant-alternates:normal;vertical-alig=
n:baseline>=E2=80=9D is the top trending celebrity =E2=80=9C...in the 90s=
=E2=80=9D</span></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-s=
ize:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);ba=
ckground-color:transparent;font-variant-numeric:normal;font-variant-east-as=
ian:normal;font-variant-alternates:normal;vertical-align:baseline;white-spa=
ce:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:=
0pt role=3Dpresentation><span style=3Dfont-size:11pt;background-color:trans=
parent;font-weight:700;font-variant-numeric:normal;font-variant-east-asian:=
normal;font-variant-alternates:normal;vertical-align:baseline>Enhypen</span=
><span style=3Dfont-size:11pt;background-color:transparent;font-variant-num=
eric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;v=
ertical-align:baseline> is the top trending entertainment search over the p=
ast day with =E2=80=9C</span><span style=3Dfont-size:11pt;background-color:=
transparent;font-weight:700;font-variant-numeric:normal;font-variant-east-a=
sian:normal;font-variant-alternates:normal;vertical-align:baseline>why is h=
eeseung leaving</span><span style=3Dfont-size:11pt;background-color:transpa=
rent;font-variant-numeric:normal;font-variant-east-asian:normal;font-varian=
t-alternates:normal;vertical-align:baseline>=E2=80=9D being a breakout sear=
ch and Heeseung is the top trending =E2=80=9C</span><span style=3Dfont-size=
:11pt;background-color:transparent;font-weight:700;font-variant-numeric:nor=
mal;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-=
align:baseline>solo album</span><span style=3Dfont-size:11pt;background-col=
or:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;f=
ont-variant-alternates:normal;vertical-align:baseline>=E2=80=9D</span></p><=
/li><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-family:=
&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transp=
arent;font-variant-numeric:normal;font-variant-east-asian:normal;font-varia=
nt-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr =
style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentati=
on><span style=3Dfont-size:11pt;background-color:transparent;font-variant-n=
umeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal=
;vertical-align:baseline>=E2=80=9C</span><a href=3Dhttps://c.gle/AEJ26qscul=
x6kIRhZCyto2it7wZHmRjdOu0PQoYQcWRJlMHrD_DO3aaZjHHZbBQFZplvU55ypTvOCNUmJebjO=
kTkssngHDelpIkVWsqsTEh-rZlnDVDyzzapFSsS7ZXgtOkdW16gI2l7ydnTQIvKJmV7Y2SsGeZQ=
5_lZnlp02SbMXww22-kELuwpRLkle93io51B337PVQorLYiJ5F0emx3b style=3Dtext-decor=
ation-line:none><span style=3Dfont-size:11pt;background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;text-decoration-line:underline;vertical-align:baseline>japane=
se sweet potato</span></a><span style=3Dfont-size:11pt;background-color:tra=
nsparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-va=
riant-alternates:normal;vertical-align:baseline>=E2=80=9D is at an all-time=
 high for the second time in 2026. =E2=80=9C</span><span style=3Dfont-size:=
11pt;background-color:transparent;font-weight:700;font-variant-numeric:norm=
al;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-a=
lign:baseline>japanese sweet potato chocolate cake</span><span style=3Dfont=
-size:11pt;background-color:transparent;font-variant-numeric:normal;font-va=
riant-east-asian:normal;font-variant-alternates:normal;vertical-align:basel=
ine>=E2=80=9D is the top trending related recipe over the past month</span>=
</p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-fa=
mily:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:t=
ransparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-=
variant-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=
=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpre=
sentation><span style=3Dfont-size:11pt;background-color:transparent;font-va=
riant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates=
:normal;vertical-align:baseline>Designer </span><a href=3Dhttps://c.gle/AEJ=
26qs_ZPYlsYAJHHYLb71gIZZHMB-bDNtWiGwW47zhclh3ooVLtclc2PQXNafIzr9m_k1JH2wnxR=
R5_E6dLKX4TgO4f3RhMKjXvXMBOs_qotfa4txjqmHFmBQr_bSpdEhsgRWG4bV3pJa_PtJQj1R1z=
6YLv1Mq7Ht8d9In11aX4KNQzfOBxHY style=3Dtext-decoration-line:none><span styl=
e=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:normal=
;font-variant-east-asian:normal;font-variant-alternates:normal;text-decorat=
ion-line:underline;vertical-align:baseline>Narciso Rodriguez </span></a><sp=
an style=3Dfont-size:11pt;background-color:transparent;font-variant-numeric=
:normal;font-variant-east-asian:normal;font-variant-alternates:normal;verti=
cal-align:baseline>is being searched more than ever before. =E2=80=9C</span=
><span style=3Dfont-size:11pt;background-color:transparent;font-weight:700;=
font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alt=
ernates:normal;vertical-align:baseline>slip wedding dresses</span><span sty=
le=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:norma=
l;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-al=
ign:baseline>=E2=80=9D spiked +375% and =E2=80=9C</span><span style=3Dfont-=
size:11pt;background-color:transparent;font-weight:700;font-variant-numeric=
:normal;font-variant-east-asian:normal;font-variant-alternates:normal;verti=
cal-align:baseline>cbk wedding dress</span><span style=3Dfont-size:11pt;bac=
kground-color:transparent;font-variant-numeric:normal;font-variant-east-asi=
an:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D =
was a breakout search over the past week</span></p></li></ul><br><p dir=3Dl=
tr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span style=3D=
"font-size:14pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(66=
,133,244);background-color:transparent;font-variant-numeric:normal;font-var=
iant-east-asian:normal;font-variant-alternates:normal;vertical-align:baseli=
ne">Google Trends Story Page</span><span style=3D"font-size:11pt;font-famil=
y:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:tran=
sparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-var=
iant-alternates:normal;vertical-align:baseline">=C2=A0</span></p><p dir=3Dl=
tr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span style=3D=
"font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,=
0,0);background-color:transparent;font-variant-numeric:normal;font-variant-=
east-asian:normal;font-variant-alternates:normal;vertical-align:baseline">T=
he 98th </span><a href=3Dhttps://c.gle/AEJ26quXzRGUNcRRkxTs8EJvlR8vPwOr7o9O=
RQq7su8VUkJLaSfnWaLhKCa5g0se1nJJGR7qqoqv134lVoaDWZKAcok7RFKrUK1KS87xiJiFt6k=
3S1F6TV8S7RPUIT4UzviD9ZzZdLck4x1PUNfsGWVEtx3K5zhJuZ9eyxXHdVB8zYQhZgDxWjtRoD=
lEtXtEkt0v_GIGk8rZ-5CWD7JwQxEArEFqXaZPf75QwbCPo5QYbgiYW_I3ZJaYkwXrgsGOKLqdi=
Eezhh9jo_6FHCKIrd2IFxOWHRwedRKKDv2nYpBdksPDj7uJ8ECLaUTimZy5nrz_V3qRUA style=
=3Dtext-decoration-line:none><span style=3D"font-size:11pt;font-family:&quo=
t;Google Sans&quot;,sans-serif;background-color:transparent;font-variant-nu=
meric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;=
text-decoration-line:underline;vertical-align:baseline">Academy Awards</spa=
n></a><span style=3D"font-size:11pt;font-family:&quot;Google Sans&quot;,san=
s-serif;color:rgb(0,0,0);background-color:transparent;font-variant-numeric:=
normal;font-variant-east-asian:normal;font-variant-alternates:normal;vertic=
al-align:baseline"> will take place on Sunday, March 15, 2026</span></p><p =
dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span s=
tyle=3D"font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color=
:rgb(0,0,0);background-color:transparent;font-variant-numeric:normal;font-v=
ariant-east-asian:normal;font-variant-alternates:normal;vertical-align:base=
line"><span style=3Dborder:none;display:inline-block;overflow:hidden;width:=
624px;height:293px><img src=3Dhttps://services.google.com/fh/files/misc/nl0=
3112026_gif.gif alt=3Dimage.jpeg width=3D563 height=3D264></span></span></p=
><br><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt=
><span style=3D"font-size:14pt;font-family:&quot;Google Sans&quot;,sans-ser=
if;color:rgb(66,133,244);background-color:transparent;font-variant-numeric:=
normal;font-variant-east-asian:normal;font-variant-alternates:normal;vertic=
al-align:baseline">Ube</span></p><ul style=3Dmargin-top:0px;margin-bottom:0=
px><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-family:&=
quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transpa=
rent;font-variant-numeric:normal;font-variant-east-asian:normal;font-varian=
t-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr s=
tyle=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentatio=
n><span style=3Dfont-size:11pt;background-color:transparent;font-variant-nu=
meric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;=
vertical-align:baseline>Search interest in </span><a href=3Dhttps://c.gle/A=
EJ26qu1Wjj-fXVtt-B4jGxTLou7b0rikAogODFLZUaaYMPSFWSEj2G38pXMojkbh6GiZvU1zze_=
hG2GVO9MurB3fs26av1Z9xfVFW4rsCp8Nww1q3mN6GyxBwAsEjwuKBe4TixSem1jwanbfZKFRT0=
sTw1w-9o6WWcLndC4lLNb4qB7M8No-KM style=3Dtext-decoration-line:none><span st=
yle=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:norm=
al;font-variant-east-asian:normal;font-variant-alternates:normal;text-decor=
ation-line:underline;vertical-align:baseline>purple yam</span></a><span sty=
le=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:norma=
l;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-al=
ign:baseline> or =E2=80=9C</span><a href=3Dhttps://c.gle/AEJ26qsrxRNcKLuQSZ=
Yof-TuPjOAWh49xwa5aZ7DNvGVtJGEWwW6Ivxfcu251jmmUL3GGp-HjRfImnMlqnDJpPj_ym838=
45A5aTrANa6GtH3DvF_3pMXA5lJTiS855Qjo0-VnLr_ikcqq-obJI9WcdzksRD4V0fgONbjD21F=
Xw style=3Dtext-decoration-line:none><span style=3Dfont-size:11pt;backgroun=
d-color:transparent;font-variant-numeric:normal;font-variant-east-asian:nor=
mal;font-variant-alternates:normal;text-decoration-line:underline;vertical-=
align:baseline>ube</span></a><span style=3Dfont-size:11pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;vertical-align:baseline>=E2=80=9D are currently =
at an all-time high in the US with =E2=80=9C</span><a href=3Dhttps://c.gle/=
AEJ26quQ8JviJDV7zpDIF3dmldzwlzqzVvZYLK8nGh8HEphU-EpiZMqNtmZ5i3DcDLccpujCbfi=
W2FhmLV4K7iJNmGnXTfpI9VqYFrUq18zebzmWGs8qjvzqj18VTqHpN0gJe7nJqtyTfTGjEfOokG=
sanRdy8MRhPF9aevlBR0N09tdas_cSBPJN3s1dhZgzV5x5_MvGP1wDKbkLIgSVBJ46A-A style=
=3Dtext-decoration-line:none><span style=3Dfont-size:11pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;text-decoration-line:underline;vertical-align:ba=
seline>what does ube taste like</span></a><span style=3Dfont-size:11pt;back=
ground-color:transparent;font-variant-numeric:normal;font-variant-east-asia=
n:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D m=
ore than doubling over the past week</span></p></li><li dir=3Dltr style=3D"=
list-style-type:disc;font-size:11pt;font-family:&quot;Google Sans&quot;,san=
s-serif;color:rgb(0,0,0);background-color:transparent;font-variant-numeric:=
normal;font-variant-east-asian:normal;font-variant-alternates:normal;vertic=
al-align:baseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;ma=
rgin-top:0pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:=
11pt;background-color:transparent;font-variant-numeric:normal;font-variant-=
east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>=
=E2=80=9C</span><a href=3Dhttps://c.gle/AEJ26qv0tbt9-qsZOKGk-qpqsTZfmDXl2fa=
mu2mxDuPY1LBTsaoizc_lAO5lnVgWORahJ0J36WsmA2guEh2mNgIJRHCdy1fXdOeSdSGJ3p-0tk=
CH6EDJtwF0PHmIaPyYk2VNOcdIqjQFJGyB2_kma4rQ0mMKN7bcmuLrQq8ZUeIir0L16pLRTGPeE=
A style=3Dtext-decoration-line:none><span style=3Dfont-size:11pt;background=
-color:transparent;font-variant-numeric:normal;font-variant-east-asian:norm=
al;font-variant-alternates:normal;text-decoration-line:underline;vertical-a=
lign:baseline>what is ube</span></a><span style=3Dfont-size:11pt;background=
-color:transparent;font-variant-numeric:normal;font-variant-east-asian:norm=
al;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D is also=
 being searched more than ever and =E2=80=9C</span><span style=3Dfont-size:=
11pt;background-color:transparent;font-weight:700;font-variant-numeric:norm=
al;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-a=
lign:baseline>is ube and taro the same</span><span style=3Dfont-size:11pt;b=
ackground-color:transparent;font-variant-numeric:normal;font-variant-east-a=
sian:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=
=9D is one of the top questions searched about ube of all time</span></p></=
li><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-family:&=
quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transpa=
rent;font-variant-numeric:normal;font-variant-east-asian:normal;font-varian=
t-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr s=
tyle=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentatio=
n><span style=3Dfont-size:11pt;background-color:transparent;font-variant-nu=
meric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;=
vertical-align:baseline>=E2=80=9C</span><span style=3Dfont-size:11pt;backgr=
ound-color:transparent;font-weight:700;font-variant-numeric:normal;font-var=
iant-east-asian:normal;font-variant-alternates:normal;vertical-align:baseli=
ne>what is ube cold foam</span><span style=3Dfont-size:11pt;background-colo=
r:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;fo=
nt-variant-alternates:normal;vertical-align:baseline>=E2=80=9D was the top-=
trending question on =E2=80=9C</span><span style=3Dfont-size:11pt;backgroun=
d-color:transparent;font-weight:700;font-variant-numeric:normal;font-varian=
t-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>=
cold foam</span><span style=3Dfont-size:11pt;background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;vertical-align:baseline>=E2=80=9D in the past month. =E2=80=
=9C</span><span style=3Dfont-size:11pt;background-color:transparent;font-we=
ight:700;font-variant-numeric:normal;font-variant-east-asian:normal;font-va=
riant-alternates:normal;vertical-align:baseline>Ube with coffee</span><span=
 style=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:n=
ormal;font-variant-east-asian:normal;font-variant-alternates:normal;vertica=
l-align:baseline>=E2=80=9D and =E2=80=9C</span><span style=3Dfont-size:11pt=
;background-color:transparent;font-weight:700;font-variant-numeric:normal;f=
ont-variant-east-asian:normal;font-variant-alternates:normal;vertical-align=
:baseline>ube with cheese</span><span style=3Dfont-size:11pt;background-col=
or:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;f=
ont-variant-alternates:normal;vertical-align:baseline>=E2=80=9D were the to=
p two trending =E2=80=9Cube with=E2=80=A6=E2=80=9D searches in the past mon=
th</span></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size:11p=
t;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);backgroun=
d-color:transparent;font-weight:700;font-variant-numeric:normal;font-varian=
t-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline;=
white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margi=
n-bottom:0pt role=3Dpresentation><span style=3Dfont-size:11pt;background-co=
lor:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;=
font-variant-alternates:normal;vertical-align:baseline>Ube Tres Leches</spa=
n><span style=3Dfont-size:11pt;background-color:transparent;font-weight:400=
;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-al=
ternates:normal;vertical-align:baseline> rose +500% in the past month, and =
=E2=80=9C</span><span style=3Dfont-size:11pt;background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;vertical-align:baseline>how to make ube extract from scratch<=
/span><span style=3Dfont-size:11pt;background-color:transparent;font-weight=
:400;font-variant-numeric:normal;font-variant-east-asian:normal;font-varian=
t-alternates:normal;vertical-align:baseline>=E2=80=9D was the top-trending =
=E2=80=9Chow to make ube=E2=80=A6=E2=80=9D</span></p></li></ul><br><p dir=
=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span styl=
e=3D"font-size:14pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rg=
b(66,133,244);background-color:transparent;font-variant-numeric:normal;font=
-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:ba=
seline">Pi(e) Day</span></p><ul style=3Dmargin-top:0px;margin-bottom:0px><l=
i dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;font-family:&quot;=
Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transparent;=
font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alt=
ernates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr style=
=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentation><s=
pan style=3Dfont-size:11pt;background-color:transparent;font-variant-numeri=
c:normal;font-variant-east-asian:normal;font-variant-alternates:normal;vert=
ical-align:baseline>Over the past month, =E2=80=9C</span><span style=3Dfont=
-size:11pt;background-color:transparent;font-weight:700;font-variant-numeri=
c:normal;font-variant-east-asian:normal;font-variant-alternates:normal;vert=
ical-align:baseline>area of a circle</span><span style=3Dfont-size:11pt;bac=
kground-color:transparent;font-variant-numeric:normal;font-variant-east-asi=
an:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D =
is the top formula searched with pi, followed by =E2=80=9Ccircumference of =
a circle=E2=80=9D</span></p></li><li dir=3Dltr style=3D"list-style-type:dis=
c;font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0=
,0,0);background-color:transparent;font-variant-numeric:normal;font-variant=
-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline;w=
hite-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin=
-bottom:0pt role=3Dpresentation><span style=3Dfont-size:11pt;background-col=
or:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;f=
ont-variant-alternates:normal;vertical-align:baseline>=E2=80=9C</span><a hr=
ef=3Dhttps://c.gle/AEJ26qsPOoLOnmozKMpym0x8mX3qSv1pEdT6jT2rykMeX9kNausKPQWw=
nR9hTQEX1U1Shd6ERy-h4wT4rqfk4-erlhqgvTR22-X4bFPia3GoYhneZ6qBhz-mQDVI4bb1d6_=
98Eyf-SHatPagq4v4ZYTBe5aR0O83KjairQD5seYXtU-SBZX-lDT2b0uFrkowEnDnmRri style=
=3Dtext-decoration-line:none><span style=3Dfont-size:11pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;text-decoration-line:underline;vertical-align:ba=
seline>memorize pi</span></a><span style=3Dfont-size:11pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;vertical-align:baseline>=E2=80=9D spikes every M=
arch, and =E2=80=9C</span><span style=3Dfont-size:11pt;background-color:tra=
nsparent;font-weight:700;font-variant-numeric:normal;font-variant-east-asia=
n:normal;font-variant-alternates:normal;vertical-align:baseline>how to memo=
rize pi fast</span><span style=3Dfont-size:11pt;background-color:transparen=
t;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-a=
lternates:normal;vertical-align:baseline>=E2=80=9D was one of the top-trend=
ing =E2=80=9C</span><span style=3Dfont-size:11pt;background-color:transpare=
nt;font-weight:700;font-variant-numeric:normal;font-variant-east-asian:norm=
al;font-variant-alternates:normal;vertical-align:baseline>how to memorize=
=E2=80=A6</span><span style=3Dfont-size:11pt;background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;vertical-align:baseline>=E2=80=9D searches in the past month<=
/span></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size:11pt;f=
ont-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-c=
olor:transparent;font-variant-numeric:normal;font-variant-east-asian:normal=
;font-variant-alternates:normal;vertical-align:baseline;white-space:pre"><p=
 dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=
=3Dpresentation><span style=3Dfont-size:11pt;background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;vertical-align:baseline>=E2=80=9C</span><span style=3Dfont-si=
ze:11pt;background-color:transparent;font-weight:700;font-variant-numeric:n=
ormal;font-variant-east-asian:normal;font-variant-alternates:normal;vertica=
l-align:baseline>lentil vegetable pie recipe</span><span style=3Dfont-size:=
11pt;background-color:transparent;font-variant-numeric:normal;font-variant-=
east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>=
=E2=80=9D was the top-trending =E2=80=9C</span><span style=3Dfont-size:11pt=
;background-color:transparent;font-weight:700;font-variant-numeric:normal;f=
ont-variant-east-asian:normal;font-variant-alternates:normal;vertical-align=
:baseline>pie recipe</span><span style=3Dfont-size:11pt;background-color:tr=
ansparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-v=
ariant-alternates:normal;vertical-align:baseline>=E2=80=9D searched in the =
past week, followed by =E2=80=9C</span><span style=3Dfont-size:11pt;backgro=
und-color:transparent;font-weight:700;font-variant-numeric:normal;font-vari=
ant-east-asian:normal;font-variant-alternates:normal;vertical-align:baselin=
e>authentic shepherd&#39;s pie recipe</span><span style=3Dfont-size:11pt;ba=
ckground-color:transparent;font-variant-numeric:normal;font-variant-east-as=
ian:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D=
</span></p></li></ul><br><p dir=3Dltr style=3Dline-height:1.38;margin-top:0=
pt;margin-bottom:0pt><span style=3D"font-size:14pt;font-family:&quot;Google=
 Sans&quot;,sans-serif;color:rgb(66,133,244);background-color:transparent;f=
ont-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alte=
rnates:normal;vertical-align:baseline">St. Patrick=E2=80=99s Day</span></p>=
<ul style=3Dmargin-top:0px;margin-bottom:0px><li dir=3Dltr style=3D"list-st=
yle-type:disc;font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif=
;color:rgb(0,0,0);background-color:transparent;font-variant-numeric:normal;=
font-variant-east-asian:normal;font-variant-alternates:normal;vertical-alig=
n:baseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-to=
p:0pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:11pt;ba=
ckground-color:transparent;font-variant-numeric:normal;font-variant-east-as=
ian:normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9C=
</span><span style=3Dfont-size:11pt;background-color:transparent;font-weigh=
t:700;font-variant-numeric:normal;font-variant-east-asian:normal;font-varia=
nt-alternates:normal;vertical-align:baseline>shamrock shake</span><span sty=
le=3Dfont-size:11pt;background-color:transparent;font-variant-numeric:norma=
l;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-al=
ign:baseline>=E2=80=9D was the top trending =E2=80=9Chow to make=E2=80=A6sh=
ake=E2=80=9D. The top trending question about the shamrock shake is =E2=80=
=9Cwhat is a shamrock shake flavor=E2=80=9D and =E2=80=9Cwhat does shamrock=
 shake taste like=E2=80=9D</span></p></li><li dir=3Dltr style=3D"list-style=
-type:disc;font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;co=
lor:rgb(0,0,0);background-color:transparent;font-variant-numeric:normal;fon=
t-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:b=
aseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0=
pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:11pt;backg=
round-color:transparent;font-variant-numeric:normal;font-variant-east-asian=
:normal;font-variant-alternates:normal;vertical-align:baseline>Search inter=
est in =E2=80=9C</span><a href=3Dhttps://c.gle/AEJ26qs_FErikXYKVkOwS2SAjqGL=
F9-6XtggZYHk6cr6CfvYIdi31sc4mQ0AhvI8jzwfnRlciOORW9AL_oco15I5v7ru0yEzP3ohE6E=
-R7Nrqdkp-wHSL0toFJrJjVWzLhJfv4QxhWTja49jG5PZr34nQ83Gl839tWQzPMQm9ZaBvGgjAo=
CKoxINOqdn6Y_bVvgs style=3Dtext-decoration-line:none><span style=3Dfont-siz=
e:11pt;background-color:transparent;font-variant-numeric:normal;font-varian=
t-east-asian:normal;font-variant-alternates:normal;text-decoration-line:und=
erline;vertical-align:baseline>what is salt beef</span></a><span style=3Dfo=
nt-size:11pt;background-color:transparent;font-variant-numeric:normal;font-=
variant-east-asian:normal;font-variant-alternates:normal;vertical-align:bas=
eline>=E2=80=9D hit an all-time high this year, and =E2=80=9C</span><span s=
tyle=3Dfont-size:11pt;background-color:transparent;font-weight:700;font-var=
iant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:=
normal;vertical-align:baseline>corned beef tacos</span><span style=3Dfont-s=
ize:11pt;background-color:transparent;font-variant-numeric:normal;font-vari=
ant-east-asian:normal;font-variant-alternates:normal;vertical-align:baselin=
e>=E2=80=9D spiked +180% in the past month</span></p></li><li dir=3Dltr sty=
le=3D"list-style-type:disc;font-size:11pt;font-family:&quot;Google Sans&quo=
t;,sans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-nu=
meric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;=
vertical-align:baseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1=
.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont=
-size:11pt;background-color:transparent;font-variant-numeric:normal;font-va=
riant-east-asian:normal;font-variant-alternates:normal;vertical-align:basel=
ine>Search interest in =E2=80=9C</span><span style=3Dfont-size:11pt;backgro=
und-color:transparent;font-weight:700;font-variant-numeric:normal;font-vari=
ant-east-asian:normal;font-variant-alternates:normal;vertical-align:baselin=
e>leprechaun beard for amigurumi</span><span style=3Dfont-size:11pt;backgro=
und-color:transparent;font-variant-numeric:normal;font-variant-east-asian:n=
ormal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D was =
the top-trending =E2=80=9C</span><span style=3Dfont-size:11pt;background-co=
lor:transparent;font-weight:700;font-variant-numeric:normal;font-variant-ea=
st-asian:normal;font-variant-alternates:normal;vertical-align:baseline>lepr=
echaun beard for=E2=80=A6</span><span style=3Dfont-size:11pt;background-col=
or:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;f=
ont-variant-alternates:normal;vertical-align:baseline>=E2=80=9D searched in=
 the past month, and =E2=80=9C</span><span style=3Dfont-size:11pt;backgroun=
d-color:transparent;font-weight:700;font-variant-numeric:normal;font-varian=
t-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>=
leprechaun beard mold</span><span style=3Dfont-size:11pt;background-color:t=
ransparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-=
variant-alternates:normal;vertical-align:baseline>=E2=80=9D broke out in se=
arch</span></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size:1=
1pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);backgro=
und-color:transparent;font-variant-numeric:normal;font-variant-east-asian:n=
ormal;font-variant-alternates:normal;vertical-align:baseline;white-space:pr=
e"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt r=
ole=3Dpresentation><span style=3Dfont-size:11pt;background-color:transparen=
t;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-a=
lternates:normal;vertical-align:baseline>=E2=80=9C</span><a href=3Dhttps://=
c.gle/AEJ26quhREdgcepBuV_NWEgqjAocz4NYLL9zysbgthOSIWKc1Auyfo-JAgeAWtgLMxDIn=
BJf1eNc-_RN6CCyR9IIiwi9vzU_eCkXSRrEOzf3RQVDmcQ1vL0B8iVj-TS2Io6RyOG3H-bhEQrO=
K6NNQge6JR3CHH4bvuLQD5QaLYdD2mbgf6jcb-_yT-SAksSOBaPT1hN3WBLdSEt2zEL_ style=
=3Dtext-decoration-line:none><span style=3Dfont-size:11pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;text-decoration-line:underline;vertical-align:ba=
seline>rainbow chain</span></a><span style=3Dfont-size:11pt;background-colo=
r:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;fo=
nt-variant-alternates:normal;vertical-align:baseline>=E2=80=9D is at a 10-y=
ear high, and =E2=80=9C</span><span style=3Dfont-size:11pt;background-color=
:transparent;font-weight:700;font-variant-numeric:normal;font-variant-east-=
asian:normal;font-variant-alternates:normal;vertical-align:baseline>paper c=
hain rainbow</span><span style=3Dfont-size:11pt;background-color:transparen=
t;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-a=
lternates:normal;vertical-align:baseline>=E2=80=9D spiked +170% in the past=
 month</span></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size=
:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);backg=
round-color:transparent;font-variant-numeric:normal;font-variant-east-asian=
:normal;font-variant-alternates:normal;vertical-align:baseline;white-space:=
pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt=
 role=3Dpresentation><span style=3Dfont-size:11pt;background-color:transpar=
ent;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant=
-alternates:normal;vertical-align:baseline>=E2=80=9C</span><span style=3Dfo=
nt-size:11pt;background-color:transparent;font-weight:700;font-variant-nume=
ric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;ve=
rtical-align:baseline>pot of gold</span><span style=3Dfont-size:11pt;backgr=
ound-color:transparent;font-variant-numeric:normal;font-variant-east-asian:=
normal;font-variant-alternates:normal;vertical-align:baseline>=E2=80=9D was=
 searched over </span><a href=3Dhttps://c.gle/AEJ26qtjFDgMe7szTvjX2hLCXo9w-=
OroASol6qZRx-IqqsFhVIszbMpxhAGJTPHPPI7Drd2ikKYbtzFjUNs7dnCIVe21pgoilmfFY3AD=
TNhQj6wVMJL36dAUgAoQ5_1bU8p9OFKSprY5Tp9WW89DHzrJkWoORSfPHSY8dof7NbGZLgp0Grf=
r2-qjZjGGE2k_kU-PWzL_GelFsQzmG2BwC0wbT5O2 style=3Dtext-decoration-line:none=
><span style=3Dfont-size:11pt;background-color:transparent;font-variant-num=
eric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;t=
ext-decoration-line:underline;vertical-align:baseline>2x more</span></a><sp=
an style=3Dfont-size:11pt;background-color:transparent;font-variant-numeric=
:normal;font-variant-east-asian:normal;font-variant-alternates:normal;verti=
cal-align:baseline> than =E2=80=9C</span><span style=3Dfont-size:11pt;backg=
round-color:transparent;font-weight:700;font-variant-numeric:normal;font-va=
riant-east-asian:normal;font-variant-alternates:normal;vertical-align:basel=
ine>leprechaun trap</span><span style=3Dfont-size:11pt;background-color:tra=
nsparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-va=
riant-alternates:normal;vertical-align:baseline>=E2=80=9D in the past three=
 months, and =E2=80=9C</span><span style=3Dfont-size:11pt;background-color:=
transparent;font-weight:700;font-variant-numeric:normal;font-variant-east-a=
sian:normal;font-variant-alternates:normal;vertical-align:baseline>pot of g=
old coloring page</span><span style=3Dfont-size:11pt;background-color:trans=
parent;font-variant-numeric:normal;font-variant-east-asian:normal;font-vari=
ant-alternates:normal;vertical-align:baseline>=E2=80=9D was the second-most=
 trending =E2=80=9Ccoloring page=E2=80=9D searched in the past week</span><=
/p></li></ul><br><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margi=
n-bottom:0pt><span style=3D"font-size:11pt;font-family:&quot;Google Sans&qu=
ot;,sans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-n=
umeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal=
;vertical-align:baseline"><span style=3Dborder:none;display:inline-block;ov=
erflow:hidden;width:624px;height:313px><img src=3Dhttps://services.google.c=
om/fh/files/misc/nl03112026_map.png alt=3Dimage.png width=3D563 height=3D28=
2></span></span></p><br><p dir=3Dltr style=3Dline-height:1.38;margin-top:0p=
t;margin-bottom:0pt></p><hr><p></p><h3 dir=3Dltr style=3Dline-height:1.2;ma=
rgin-top:16pt;margin-bottom:4pt><span style=3D"font-size:14pt;font-family:&=
quot;Google Sans&quot;,sans-serif;color:rgb(66,133,244);background-color:tr=
ansparent;font-weight:400;font-variant-numeric:normal;font-variant-east-asi=
an:normal;font-variant-alternates:normal;vertical-align:baseline">Mark Your=
 Calendars</span><span style=3D"font-size:14pt;font-family:&quot;Google San=
s&quot;,sans-serif;color:rgb(52,168,83);background-color:transparent;font-w=
eight:400;font-variant-numeric:normal;font-variant-east-asian:normal;font-v=
ariant-alternates:normal;vertical-align:baseline"><br><br></span></h3><div =
dir=3Dltr style=3Dmargin-left:0.75pt align=3Dleft><table style=3Dborder:non=
e;border-collapse:collapse><colgroup><col width=3D206><col width=3D210><col=
 width=3D207></colgroup><tbody><tr style=3Dheight:28.8pt><td style=3D"borde=
r-bottom:1pt solid rgb(225,227,225);border-top:1pt solid rgb(225,227,225);v=
ertical-align:top;padding:5pt;overflow:hidden"><p dir=3Dltr style=3Dline-he=
ight:1.38;text-align:center;margin-top:0pt;margin-bottom:0pt><span style=3D=
"font-size:11pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,=
0,0);background-color:transparent;font-weight:700;font-variant-numeric:norm=
al;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-a=
lign:baseline">Eid Al Fitr</span></p><p dir=3Dltr style=3Dline-height:1.38;=
text-align:center;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size=
:9pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);backgr=
ound-color:transparent;font-style:italic;font-variant-numeric:normal;font-v=
ariant-east-asian:normal;font-variant-alternates:normal;vertical-align:base=
line">March 20, 2026</span></p></td><td style=3D"border-bottom:1pt solid rg=
b(225,227,225);border-top:1pt solid rgb(225,227,225);vertical-align:top;pad=
ding:5pt;overflow:hidden"><p dir=3Dltr style=3Dline-height:1.38;text-align:=
center;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size:11pt;font-=
family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color=
:transparent;font-weight:700;font-variant-numeric:normal;font-variant-east-=
asian:normal;font-variant-alternates:normal;vertical-align:baseline">Spring=
 Equinox</span><span style=3D"font-size:11pt;font-family:&quot;Google Sans&=
quot;,sans-serif;color:rgb(0,0,0);background-color:transparent;font-weight:=
700;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant=
-alternates:normal;vertical-align:baseline"><br></span><span style=3D"font-=
size:9pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);ba=
ckground-color:transparent;font-style:italic;font-variant-numeric:normal;fo=
nt-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:=
baseline">March 20, 2026</span></p></td><td style=3D"border-bottom:1pt soli=
d rgb(225,227,225);border-top:1pt solid rgb(225,227,225);vertical-align:top=
;padding:5pt;overflow:hidden"><p dir=3Dltr style=3Dline-height:1.38;text-al=
ign:center;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size:11pt;f=
ont-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-c=
olor:transparent;font-weight:700;font-variant-numeric:normal;font-variant-e=
ast-asian:normal;font-variant-alternates:normal;vertical-align:baseline">Ma=
sters Tournament</span><span style=3D"font-size:11pt;font-family:&quot;Goog=
le Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transparent;font=
-weight:700;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;vertical-align:baseline"><br></span><span style=
=3D"font-size:9pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(=
0,0,0);background-color:transparent;font-style:italic;font-variant-numeric:=
normal;font-variant-east-asian:normal;font-variant-alternates:normal;vertic=
al-align:baseline">April 6, 2026</span></p></td></tr><tr style=3Dheight:28.=
8pt><td style=3D"border-bottom:1pt solid rgb(225,227,225);border-top:1pt so=
lid rgb(225,227,225);vertical-align:top;padding:5pt;overflow:hidden"><p dir=
=3Dltr style=3Dline-height:1.38;text-align:center;margin-top:0pt;margin-bot=
tom:0pt><span style=3D"font-size:10pt;font-family:&quot;Google Sans&quot;,s=
ans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-numeri=
c:normal;font-variant-east-asian:normal;font-variant-alternates:normal;vert=
ical-align:baseline">+35% past week</span></p><p dir=3Dltr style=3Dline-hei=
ght:1.38;text-align:center;margin-top:0pt;margin-bottom:0pt><span style=3D"=
font-size:10pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0=
,0);background-color:transparent;font-variant-numeric:normal;font-variant-e=
ast-asian:normal;font-variant-alternates:normal;vertical-align:baseline">+1=
45% past month</span></p><p dir=3Dltr style=3Dline-height:1.38;text-align:c=
enter;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size:10pt;font-f=
amily:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;vertical-align:baseline">+110% same week last ye=
ar</span></p></td><td style=3D"border-bottom:1pt solid rgb(225,227,225);bor=
der-top:1pt solid rgb(225,227,225);vertical-align:top;padding:5pt;overflow:=
hidden"><p dir=3Dltr style=3Dline-height:1.38;text-align:center;margin-top:=
0pt;margin-bottom:0pt><span style=3D"font-size:10pt;font-family:&quot;Googl=
e Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:transparent;font-=
variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternat=
es:normal;vertical-align:baseline">+15% past week</span></p><p dir=3Dltr st=
yle=3Dline-height:1.38;text-align:center;margin-top:0pt;margin-bottom:0pt><=
span style=3D"font-size:10pt;font-family:&quot;Google Sans&quot;,sans-serif=
;color:rgb(0,0,0);background-color:transparent;font-variant-numeric:normal;=
font-variant-east-asian:normal;font-variant-alternates:normal;vertical-alig=
n:baseline">+100% past month</span></p><p dir=3Dltr style=3Dline-height:1.3=
8;text-align:center;margin-top:0pt;margin-bottom:0pt><span style=3D"font-si=
ze:10pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);bac=
kground-color:transparent;font-variant-numeric:normal;font-variant-east-asi=
an:normal;font-variant-alternates:normal;vertical-align:baseline">-1% same =
week last year</span></p></td><td style=3D"border-bottom:1pt solid rgb(225,=
227,225);border-top:1pt solid rgb(225,227,225);vertical-align:top;padding:5=
pt;overflow:hidden"><p dir=3Dltr style=3Dline-height:1.38;text-align:center=
;margin-top:0pt;margin-bottom:0pt><span style=3D"font-size:10pt;font-family=
:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-color:trans=
parent;font-variant-numeric:normal;font-variant-east-asian:normal;font-vari=
ant-alternates:normal;vertical-align:baseline">+20% past week</span></p><p =
dir=3Dltr style=3Dline-height:1.38;text-align:center;margin-top:0pt;margin-=
bottom:0pt><span style=3D"font-size:10pt;font-family:&quot;Google Sans&quot=
;,sans-serif;color:rgb(0,0,0);background-color:transparent;font-variant-num=
eric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;v=
ertical-align:baseline">+30% past month</span></p><p dir=3Dltr style=3Dline=
-height:1.38;text-align:center;margin-top:0pt;margin-bottom:0pt><span style=
=3D"font-size:10pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb=
(0,0,0);background-color:transparent;font-variant-numeric:normal;font-varia=
nt-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline=
">-2% same week last year</span></p></td></tr></tbody></table></div><br><p =
dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt></p><hr=
><p></p><br><div dir=3Dltr style=3Dmargin-left:0pt align=3Dleft><table styl=
e=3Dborder:none;border-collapse:collapse;table-layout:fixed;width:468pt><co=
lgroup><col></colgroup><tbody><tr style=3Dheight:0pt><td style=3Dborder-wid=
th:1pt;border-style:solid;border-color:rgb(248,249,250);vertical-align:top;=
background-color:rgb(248,249,250);padding:5pt;overflow:hidden><p dir=3Dltr =
style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt><span style=3D"fo=
nt-size:8.5pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(67,6=
7,67);background-color:transparent;font-variant-numeric:normal;font-variant=
-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline">=
Notes</span></p><ul style=3Dmargin-top:0px;margin-bottom:0px><li dir=3Dltr =
style=3D"list-style-type:disc;font-size:8.5pt;font-family:&quot;Google Sans=
&quot;,sans-serif;color:rgb(67,67,67);background-color:transparent;font-var=
iant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:=
normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr style=3Dline-h=
eight:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentation><span style=
=3Dfont-size:8.5pt;background-color:transparent;font-variant-numeric:normal=
;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-ali=
gn:baseline>United States data unless stated otherwise and is accurate at t=
he time of publication</span></p></li><li dir=3Dltr style=3D"list-style-typ=
e:disc;font-size:8.5pt;font-family:&quot;Google Sans&quot;,sans-serif;color=
:rgb(67,67,67);background-color:transparent;font-variant-numeric:normal;fon=
t-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:b=
aseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0=
pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:8.5pt;back=
ground-color:transparent;font-style:italic;font-variant-numeric:normal;font=
-variant-east-asian:normal;font-variant-alternates:normal;vertical-align:ba=
seline>Breakout:</span><span style=3Dfont-size:8.5pt;background-color:trans=
parent;font-variant-numeric:normal;font-variant-east-asian:normal;font-vari=
ant-alternates:normal;vertical-align:baseline> search terms had a tremendou=
s increase, in some cases because these terms are new and had few (if any) =
prior searches</span></p></li><li dir=3Dltr style=3D"list-style-type:disc;f=
ont-size:8.5pt;font-family:&quot;Google Sans&quot;,sans-serif;color:rgb(67,=
67,67);background-color:transparent;font-variant-numeric:normal;font-varian=
t-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline;=
white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margi=
n-bottom:0pt role=3Dpresentation><span style=3Dfont-size:8.5pt;background-c=
olor:transparent;font-style:italic;font-variant-numeric:normal;font-variant=
-east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>T=
op or Most Searched:</span><span style=3Dfont-size:8.5pt;background-color:t=
ransparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-=
variant-alternates:normal;vertical-align:baseline> search terms that rank h=
ighest by search volume for a given timeframe and location</span></p></li><=
li dir=3Dltr style=3D"list-style-type:disc;font-size:8.5pt;font-family:&quo=
t;Google Sans&quot;,sans-serif;color:rgb(67,67,67);background-color:transpa=
rent;font-variant-numeric:normal;font-variant-east-asian:normal;font-varian=
t-alternates:normal;vertical-align:baseline;white-space:pre"><p dir=3Dltr s=
tyle=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dpresentatio=
n><span style=3Dfont-size:8.5pt;background-color:transparent;font-style:ita=
lic;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant=
-alternates:normal;vertical-align:baseline>Trending Searches</span><span st=
yle=3Dfont-size:8.5pt;background-color:transparent;font-variant-numeric:nor=
mal;font-variant-east-asian:normal;font-variant-alternates:normal;vertical-=
align:baseline>: search terms that had the highest spike in traffic over a =
given time period as compared with the previous equivalent period=C2=A0</sp=
an></p></li><li dir=3Dltr style=3D"list-style-type:disc;font-size:8.5pt;fon=
t-family:&quot;Google Sans&quot;,sans-serif;color:rgb(0,0,0);background-col=
or:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;f=
ont-variant-alternates:normal;vertical-align:baseline;white-space:pre"><p d=
ir=3Dltr style=3Dline-height:1.38;margin-top:0pt;margin-bottom:0pt role=3Dp=
resentation><span style=3Dfont-size:8.5pt;color:rgb(67,67,67);background-co=
lor:transparent;font-variant-numeric:normal;font-variant-east-asian:normal;=
font-variant-alternates:normal;vertical-align:baseline>For more information=
 about our methodology and how to interpret the data, please read our</span=
><a href=3Dhttps://c.gle/AEJ26qvtRHDO6u-OJ561G-SRj7QNC18F7j4zWXlqiGSgB5xZu0=
CmqIsy4nNkMJ04jvVGsofwlyjtCGp9wf-VbvY9T6toSZCngnNzBrgbDF2QVWCBR9Dc04Ks2_DUF=
tXpCbmCtcP0LWW6iS1imDgBP3ME7RM1SMwmkke_6So3596egk16RKmIQrQ style=3Dtext-dec=
oration-line:none><span style=3Dfont-size:8.5pt;color:rgb(67,67,67);backgro=
und-color:transparent;font-variant-numeric:normal;font-variant-east-asian:n=
ormal;font-variant-alternates:normal;text-decoration-line:underline;vertica=
l-align:baseline> </span><span style=3Dfont-size:8.5pt;background-color:tra=
nsparent;font-variant-numeric:normal;font-variant-east-asian:normal;font-va=
riant-alternates:normal;text-decoration-line:underline;vertical-align:basel=
ine>FAQs</span></a><span style=3Dfont-size:8.5pt;background-color:transpare=
nt;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-=
alternates:normal;vertical-align:baseline> </span><span style=3Dfont-size:8=
.5pt;color:rgb(67,67,67);background-color:transparent;font-variant-numeric:=
normal;font-variant-east-asian:normal;font-variant-alternates:normal;vertic=
al-align:baseline>and</span><span style=3Dfont-size:8.5pt;background-color:=
transparent;font-variant-numeric:normal;font-variant-east-asian:normal;font=
-variant-alternates:normal;vertical-align:baseline> </span><a href=3Dhttps:=
//c.gle/AEJ26qtp6WELFFv8g9l27x6JR83sgsbzp7iIorx9VdpHJ3xqoogtnbLuvMqeblahQu_=
1UKYtDNfQiKTFExXzIXmcaSG63nzHI2y8vYCaNQpMpH4hHwSkeItAAKE2Bh4NRoEZDsjnlVH4MJ=
ZZ0ne-ocRQ7QYiAXrMasJmUENFb9tBz5AjKxe87oPS3Oq9khs7ViFjibD91-Z7DhQagoySJuA s=
tyle=3Dtext-decoration-line:none><span style=3Dfont-size:8.5pt;background-c=
olor:transparent;font-variant-numeric:normal;font-variant-east-asian:normal=
;font-variant-alternates:normal;text-decoration-line:underline;vertical-ali=
gn:baseline>learn more here</span></a></p></li><li dir=3Dltr style=3D"list-=
style-type:disc;font-size:8.5pt;font-family:&quot;Google Sans&quot;,sans-se=
rif;color:rgb(67,67,67);background-color:transparent;font-variant-numeric:n=
ormal;font-variant-east-asian:normal;font-variant-alternates:normal;vertica=
l-align:baseline;white-space:pre"><p dir=3Dltr style=3Dline-height:1.38;mar=
gin-top:0pt;margin-bottom:0pt role=3Dpresentation><span style=3Dfont-size:8=
.5pt;background-color:transparent;font-variant-numeric:normal;font-variant-=
east-asian:normal;font-variant-alternates:normal;vertical-align:baseline>If=
 you=E2=80=99d like to use Trends data, please read: </span><a href=3Dhttps=
://c.gle/AEJ26qsMZirQSIbt7V9FC6SUwW6UcU_5qUKDkLXX2gx00sSCMmOyyOTgEtb_N8u66E=
Jgo2pPCEaCyDEApuzvAe2JzKsJAOAx29l_yq9YrDiO1KZXhnrV5Z4lZpzjvF1QmJHULv5vzgj2d=
CCe-jtLlqYfhhbZl0M style=3Dtext-decoration-line:none><span style=3Dfont-siz=
e:8.5pt;background-color:transparent;font-variant-numeric:normal;font-varia=
nt-east-asian:normal;font-variant-alternates:normal;text-decoration-line:un=
derline;vertical-align:baseline>How to use and cite Trends data</span></a><=
/p></li></ul></td></tr></tbody></table></div><br></span></div>

Google LLC 1600 Amphitheatre Parkway, Mountain View, CA 94043.<br><br>

This email was sent to luke@modrynstudio.com because you have subscribed to=
 the Google Trends Daily Trending Newsletter. If you do not wish to receive=
 such emails in the future, please <a href=3Dhttps://myaccount.google.com/c=
ommunication-preferences/unsubscribe/gt/AEJ26qvFQDVfgZ9x8sgcrfxgxh-cvFd46zX=
hdGbiEJvjbDRXneH3m_bnEulR9GPTGR6zVW1eRRZ0WZjJE1cuhUvxj1hJvcaVsUGEVp_e9pX7E0=
UmjDHXnrFLDFdDjOJSI_AfgEUQ4QYCzx2rsEypBq0vXW8BeMSc_ZAsU7DwdbE2WWYWoLBPctACz=
JxfKlqHcpYNIwxa2uOPXJk3iY3VAz1vJUU18QsRR4BrWKiq6j1DwDYeLiZVdg?utm_source=3D=
gm&amp;utm_medium=3Demail&amp;auto=3Dtrue>unsubscribe here</a>
--00000000000082e44e064cc3829c--