# Production Logging Guide

## Overview

The RAG system uses **multi-level logging** with separate files for different log levels. This makes troubleshooting faster and monitoring easier.

## Log File Structure

```
logs/
├── rag_indexing_20260122_103015_all.log      # Everything (DEBUG+)
├── rag_indexing_20260122_103015_info.log     # Summary (INFO+)
├── rag_indexing_20260122_103015_error.log    # Issues only (WARNING+)
├── rag_query_20260122_103520_all.log         # Query - Everything
├── rag_query_20260122_103520_info.log        # Query - Summary
└── rag_query_20260122_103520_error.log       # Query - Issues
```

## Log Levels and Routing

```
                    ┌─────────────────────────┐
                    │   Python Code           │
                    │   logger.debug("...")   │
                    │   logger.info("...")    │
                    │   logger.warning("...")  │
                    │   logger.error("...")   │
                    └──────────┬──────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
    ┌───────────────────┐         ┌──────────────────┐
    │  Log Handlers     │         │   Console        │
    │  (File Writers)   │         │   (Screen)       │
    └────────┬──────────┘         └──────────────────┘
             │                     Shows: INFO+
             │
    ┌────────┴─────────────────────────────┐
    │                                      │
    ▼                                      ▼
┌─────────────────┐              ┌──────────────────┐
│  *_all.log      │              │  *_info.log      │
│  Level: DEBUG   │              │  Level: INFO     │
│                 │              │                  │
│  ✓ DEBUG        │              │  ✗ DEBUG         │
│  ✓ INFO         │              │  ✓ INFO          │
│  ✓ WARNING      │              │  ✓ WARNING       │
│  ✓ ERROR        │              │  ✓ ERROR         │
└─────────────────┘              └──────────────────┘

                    ┌──────────────────┐
                    │  *_error.log     │
                    │  Level: WARNING  │
                    │                  │
                    │  ✗ DEBUG         │
                    │  ✗ INFO          │
                    │  ✓ WARNING       │
                    │  ✓ ERROR         │
                    └──────────────────┘
```

## When to Use Each Log File

### 1. All Log (`*_all.log`)

**Use When:**
- Debugging production issues
- Need complete execution trace
- Investigating performance bottlenecks
- Compliance audits
- Root cause analysis

**Contains:**
- Every single log message (DEBUG, INFO, WARNING, ERROR)
- Full stack traces
- API request/response details
- Embedding dimensions
- Chunk sizes
- Token counts

**Example:**
```bash
# See everything that happened
tail -f logs/rag_indexing_20260122_103015_all.log

# Search for specific chunk
grep "chunk_id: 5" logs/rag_indexing_20260122_103015_all.log
```

### 2. Info Log (`*_info.log`)

**Use When:**
- Quick status check (Did it work?)
- Monitoring dashboards
- Daily operations review
- Performance summaries
- Success verification

**Contains:**
- High-level progress (STEP 1, STEP 2, etc.)
- Counts (documents loaded, chunks created)
- Durations (total time elapsed)
- Success confirmations

**Example:**
```bash
# Quick check - did it finish?
tail -20 logs/rag_indexing_20260122_103015_info.log

# How long did it take?
grep "duration" logs/rag_indexing_20260122_103015_info.log
```

### 3. Error Log (`*_error.log`)

**Use When:**
- Something went wrong
- Setting up alerts/monitoring
- Incident response
- Finding what failed

**Contains:**
- Only WARNING and ERROR messages
- Full stack traces for errors
- Connection failures
- API errors
- Validation warnings

**Example:**
```bash
# Check if anything went wrong (empty = success!)
cat logs/rag_indexing_20260122_103015_error.log

# Set up monitoring alert
if [ -s logs/rag_indexing_*_error.log ]; then
  echo "ALERT: Errors detected!"
fi
```

## Production Best Practices

### 1. Log Rotation

Keep logs organized by date:

```bash
# Create daily directories
logs/
├── 2026-01-22/
│   ├── rag_indexing_103015_all.log
│   ├── rag_indexing_103015_info.log
│   └── rag_indexing_103015_error.log
└── 2026-01-23/
    └── ...
```

### 2. Log Retention Policy

Recommended retention:

| Log Type | Keep For | Why |
|----------|----------|-----|
| `*_error.log` | 90 days | Incident analysis, compliance |
| `*_info.log` | 30 days | Recent operations review |
| `*_all.log` | 7 days | Debug recent issues, then archive |

### 3. Monitoring Setup

**Alerting on Errors:**
```bash
#!/bin/bash
# check_errors.sh - Run every 5 minutes via cron

ERROR_LOG=$(ls -t logs/*_error.log | head -1)

if [ -s "$ERROR_LOG" ]; then
  # Error log has content - send alert
  echo "ALERT: Errors detected in $ERROR_LOG"
  cat "$ERROR_LOG" | mail -s "RAG System Error" admin@example.com
fi
```

**Dashboard Metrics:**
```bash
# Extract metrics from info logs
grep "Total duration" logs/*_info.log | awk '{print $NF}'
grep "Documents loaded" logs/*_info.log | awk '{print $NF}'
grep "Chunks created" logs/*_info.log | awk '{print $NF}'
```

### 4. Log Analysis Commands

**Find slow executions:**
```bash
grep "Total duration" logs/*_info.log | awk '$NF > 30'
```

**Count total documents processed today:**
```bash
grep "Documents loaded" logs/rag_indexing_$(date +%Y%m%d)_*_info.log | \
  awk '{sum += $NF} END {print sum}'
```

**Check for connection issues:**
```bash
grep -i "connection" logs/*_error.log
```

**See all warnings:**
```bash
grep "WARNING" logs/*_error.log
```

## Log File Sizes

Typical sizes for reference:

| Operation | All Log | Info Log | Error Log |
|-----------|---------|----------|-----------|
| Index 1 doc (12 chunks) | 2,450 lines (~180 KB) | 48 lines (~4 KB) | 0 lines (0 KB) |
| Index 10 docs (120 chunks) | 24,500 lines (~1.8 MB) | 480 lines (~40 KB) | 0 lines (0 KB) |
| Query (1 question) | 125 lines (~12 KB) | 25 lines (~2 KB) | 0 lines (0 KB) |
| Failed indexing | 1,200 lines (~90 KB) | 30 lines (~3 KB) | 15 lines (~2 KB) |

## Troubleshooting Workflow

```
┌─────────────────────────┐
│  Something went wrong?  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  1. Check *_error.log   │  ← Start here!
│  Is it empty?           │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼ Yes           ▼ No
┌─────────┐   ┌──────────────┐
│ Success │   │ Found issue! │
│ Exit    │   │ Read error   │
└─────────┘   └──────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Need context?  │
            │ Check *_all.log│
            └────────────────┘
```

## Example: Debugging a Failed Run

```bash
# Step 1: Quick check - did it fail?
$ cat logs/rag_indexing_20260122_103015_error.log

2026-01-22 10:30:42 - __main__ - ERROR - Failed to insert chunk 5: Connection timeout
Traceback (most recent call last):
  File "simple_rag.py", line 285, in step4_vector_database_storage
    collection.data.insert(...)

# Step 2: Get context - what was happening before?
$ grep -B 10 "Failed to insert chunk 5" logs/rag_indexing_20260122_103015_all.log

2026-01-22 10:30:40 - __main__ - DEBUG - Inserted chunk 3
2026-01-22 10:30:41 - __main__ - DEBUG - Inserted chunk 4
2026-01-22 10:30:42 - __main__ - INFO - Insert progress: 5/12 chunks
2026-01-22 10:30:42 - __main__ - ERROR - Failed to insert chunk 5: Connection timeout

# Step 3: Check if it's a pattern
$ grep -c "Connection timeout" logs/*_error.log
3  # Multiple timeouts - network issue!
```

## Summary

✅ **Three log files per execution**: `*_all.log`, `*_info.log`, `*_error.log`

✅ **Start with error log**: Empty = success, has content = investigate

✅ **Use info log** for monitoring and quick status

✅ **Use all log** for detailed debugging

✅ **Set up alerts** on error log content

✅ **Rotate and archive** based on retention policy
