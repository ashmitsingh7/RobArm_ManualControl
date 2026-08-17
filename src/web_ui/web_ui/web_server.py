#!/usr/bin/env python3
"""Web server for the robotic arm control UI."""

import asyncio
import json
import sys
from pathlib import Path

from aiohttp import web
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class WebServerNode(Node):
    """ROS2 node that holds the aiohttp app and publishes to /user_input."""

    def __init__(self):
        super().__init__('web_server')
        self.publisher = self.create_publisher(String, '/user_input', 10)
        self.get_logger().info('Web server node started')

        # Static file directory
        self.static_dir = Path(__file__).parent.parent / 'static'
        if not self.static_dir.exists():
            self.static_dir = Path('/opt/ros/humble/share/web_ui/static')

    def publish_key(self, key: str):
        msg = String()
        msg.data = key.strip().lower()
        self.publisher.publish(msg)
        self.get_logger().info(f'Published to /user_input: {msg.data}')


async def index_handler(request):
    """Serve the main UI page."""
    static_dir = request.app['static_dir']
    index_path = static_dir / 'index.html'
    if index_path.exists():
        return web.FileResponse(index_path)
    return web.Response(text='UI not built. Run colcon build.', status=404)


async def websocket_handler(request):
    """WebSocket endpoint for UI → ROS2 key commands."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    node = request.app['ros_node']
    node.get_logger().info('WebSocket client connected')

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                key = data.get('key', '')
                if key:
                    node.publish_key(key)
            except json.JSONDecodeError:
                node.get_logger().warn(f'Invalid WS message: {msg.data}')
        elif msg.type == web.WSMsgType.ERROR:
            node.get_logger().error(f'WS error: {ws.exception()}')

    node.get_logger().info('WebSocket client disconnected')
    return ws


def create_app(ros_node, static_dir):
    """Create aiohttp application."""
    app = web.Application()
    app['ros_node'] = ros_node
    app['static_dir'] = static_dir

    # Routes
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/static/', path=static_dir, name='static')

    return app


async def run_server(ros_node, host='0.0.0.0', port=8080):
    """Run the aiohttp server."""
    # Use ament_index to find the package share directory
    try:
        from ament_index_python.packages import get_package_share_directory
        static_dir = Path(get_package_share_directory('web_ui')) / 'static'
    except Exception:
        static_dir = Path(__file__).parent.parent / 'static'
        if not static_dir.exists():
            static_dir = Path('/opt/ros/humble/share/web_ui/static')

    app = create_app(ros_node, static_dir)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    ros_node.get_logger().info(f'Web server running at http://{host}:{port}')
    ros_node.get_logger().info(f'Static dir: {static_dir}')

    # Keep running until shutdown
    try:
        while rclpy.ok():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()


def main(args=None):
    rclpy.init(args=args)

    # Parse port from args
    port = 8080
    if args:
        for arg in args:
            if arg.startswith('port:'):
                try:
                    port = int(arg.split(':')[1])
                except (IndexError, ValueError):
                    pass

    node = WebServerNode()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    spin_task = None

    try:
        spin_task = loop.create_task(spin_ros(node))
        loop.run_until_complete(run_server(node, port=port))
    except KeyboardInterrupt:
        pass
    finally:
        if spin_task is not None:
            spin_task.cancel()
            loop.run_until_complete(asyncio.gather(spin_task, return_exceptions=True))
        node.destroy_node()
        rclpy.shutdown()
        loop.close()


async def spin_ros(node):
    """Spin ROS2 in async loop."""
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    main(sys.argv[1:])
