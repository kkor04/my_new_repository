SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract PenTestAuditTrail {
    struct CommandLog {
        bytes32 toolHash;
        bytes32 commandHash;
        bytes32 paramsHash;
        uint256 timestamp;
        address executor;
    }

    mapping(bytes32 => CommandLog) public logs;
    uint256 public logCount;

    event CommandLogged(
        bytes32 indexed logId,
        bytes32 toolHash,
        bytes32 commandHash,
        bytes32 paramsHash,
        uint256 timestamp,
        address executor
    );

    function logCommand(
        bytes32 _toolHash,
        bytes32 _commandHash,
        bytes32 _paramsHash
    ) external {
        bytes32 logId = keccak256(abi.encodePacked(
            _toolHash,
            _commandHash,
            _paramsHash,
            block.timestamp,
            msg.sender
        ));

        logs[logId] = CommandLog({
            toolHash: _toolHash,
            commandHash: _commandHash,
            paramsHash: _paramsHash,
            timestamp: block.timestamp,
            executor: msg.sender
        });

        logCount++;
        emit CommandLogged(logId, _toolHash, _commandHash, _paramsHash, block.timestamp, msg.sender);
    }

    function verifyCommand(
        bytes32 _toolHash,
        bytes32 _commandHash,
        bytes32 _paramsHash,
        uint256 _timestamp,
        address _executor
    ) external view returns (bool) {
        bytes32 logId = keccak256(abi.encodePacked(
            _toolHash,
            _commandHash,
            _paramsHash,
            _timestamp,
            _executor
        ));
        return logs[logId].timestamp > 0;
    }

    // Fallback function to prevent accidental Ether transfers
    fallback() external payable {
        revert("Ether transfers not allowed");
    }

    receive() external payable {
        revert("Ether transfers not allowed");
    }
}
