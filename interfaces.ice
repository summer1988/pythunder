#pragma once


[["python:package:rpc"]]
module interfaces {
    interface PyThunderBaseServant {
        ["amd"] idempotent void startProject(string pid, out bool status);
        ["amd"] idempotent void holdProject(string pid, out bool status);
        ["amd"] idempotent void resumeProject(string pid, out bool status);
        ["amd"] idempotent void stopProject(string pid, out bool status);
    };

    interface Fetcher extends PyThunderBaseServant {
        ["amd"] idempotent void networkStatistics(string pid, out string info);
    };
};