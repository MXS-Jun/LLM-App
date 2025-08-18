from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import shutil

IMAGE_DIR = Path(__file__).parent / "images"
MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class ImageRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/images/"):
            self._handle_image_request()
        else:
            self._send_error(404, "Resource not found")

    def _handle_image_request(self):
        """处理图片请求的核心逻辑"""
        file_name = self._extract_file_name()
        if not file_name:
            return self._send_error(400, "Missing file name")

        image_path = IMAGE_DIR / file_name
        if not self._is_valid_path(image_path):
            return self._send_error(404, "Invalid path")

        if not image_path.exists() or not image_path.is_file():
            return self._send_error(404, f"Image not found: {file_name}")

        if not self._is_supported_format(image_path):
            return self._send_error(404, f"Unsupported format: {image_path.suffix}")

        self._serve_image(image_path)

    def _extract_file_name(self):
        """安全提取文件名"""
        return self.path.split("/images/", 1)[-1]

    def _is_valid_path(self, path):
        """防止路径遍历攻击的安全检查"""
        try:
            # 规范化路径并检查是否在IMAGE_DIR内
            resolved = path.resolve()
            return resolved.is_relative_to(IMAGE_DIR.resolve())
        except (ValueError, RuntimeError):
            return False

    def _is_supported_format(self, path):
        """检查文件格式是否支持"""
        return path.suffix.lower() in MIME_TYPES

    def _serve_image(self, image_path):
        """流式传输图片文件"""
        try:
            with open(image_path, "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", MIME_TYPES[image_path.suffix.lower()])
                self.send_header("Content-Length", str(image_path.stat().st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
        except Exception as e:
            self.log_error(f"Failed to serve {image_path}: {str(e)}")
            # 响应头已发送，无法更改状态码，仅记录错误

    def _send_error(self, code, message=""):
        """统一错误处理"""
        self.send_response(code)
        self.end_headers()
        self.log_error(f"Error {code}: {message}")


if __name__ == "__main__":
    host = "localhost"
    port = 8000
    server = HTTPServer((host, port), ImageRequestHandler)
    print(f"[INFO] Server started at http://{host}:{port}")
    print(f"[INFO] Serving images from: {IMAGE_DIR.resolve()}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server shutdown initiated")
        server.shutdown()
        print("[INFO] Server stopped gracefully")
