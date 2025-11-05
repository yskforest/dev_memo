#include "stdafx.h"

#include <winsvc.h>

#include "scan/std.h"

#include "scan/com.h"

extern "C" {
#include "scan/CanInjector.h"
int COMgetdata(int fmt, ...);
};
}

TEST(CANSkipToPhaseWithoutRegistration, CANSkipToPhase) {
    BYTE phase_no = 10;
    int ret = CANSkipToPhase(phase_no);
    EXPECT_EQ(ret, -1);
}

TEST(CRSContrastEntityTest, SetPhaseSkipDelayTime) {
    int set_delay_time = 8;

    CRSContrastEntity ce;
    ce.SetPhaseSkipDelayTime(set_delay_time);
    int get_delay_time = ce.GetPhaseSkipDelayTime();
    EXPECT_EQ(set_delay_time, get_delay_time);
}

TEST(CRSContrastEntityTest, GetPhaseSkipDelayTime) {
    int set_delay_time = 8;

    CRSContrastEntity ce;
    ce.SetPhaseSkipDelayTime(set_delay_time);
    int get_delay_time = ce.GetPhaseSkipDelayTime();
    EXPECT_EQ(set_delay_time, get_delay_time);
}