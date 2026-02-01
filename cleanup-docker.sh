#!/bin/bash
# Docker Cleanup Script for EC2
# Run this on your EC2 instance to free up disk space

echo "=========================================="
echo "Docker Cleanup - Freeing Disk Space"
echo "=========================================="

# Check current disk usage
echo "Current disk usage:"
df -h /

echo ""
echo "Cleaning up Docker resources..."

# Remove stopped containers
echo "✓ Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "✓ Removing unused images..."
docker image prune -a -f

# Remove unused volumes
echo "✓ Removing unused volumes..."
docker volume prune -f

# Remove build cache
echo "✓ Removing build cache..."
docker builder prune -a -f

# Remove dangling images
echo "✓ Removing dangling images..."
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

echo ""
echo "After cleanup:"
df -h /

echo ""
echo "=========================================="
echo "✓ Cleanup complete!"
echo "=========================================="
