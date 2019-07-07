#include <stdio.h>
#include <string.h>

#import <IOKit/IOKitLib.h>

#define kGetSensorReadingID 0
#define calibrationConstant 25064


static uint64_t max (uint64_t x, uint64_t y) {
    return x ^ ((x ^ y) & -(x < y));
};

uint64_t readSensor () {
    io_connect_t dataPort;
    kern_return_t kr = KERN_FAILURE;
    io_service_t serviceObject;

    uint32_t outputCount = 2;
    uint64_t values[outputCount];

    serviceObject = IOServiceGetMatchingService(kIOMasterPortDefault, IOServiceMatching("AppleLMUController"));
    if (serviceObject) {
        kr = IOServiceOpen(serviceObject, mach_task_self(), 0, &dataPort);
    }

    IOObjectRelease(serviceObject);

    if (kr == KERN_SUCCESS) {
        kr = IOConnectCallMethod(dataPort, kGetSensorReadingID, nil, 0, nil, 0, values, &outputCount, nil, 0);
        IOServiceClose(dataPort);
        return max(values[0], values[1]) / calibrationConstant;
    }
    else {
        IOServiceClose(dataPort);
        return -1;
    }
}
