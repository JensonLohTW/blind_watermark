"""
命令列工具模組

提供命令列介面用於水印嵌入與提取
"""
import sys
import logging
from optparse import OptionParser
from typing import Optional

from .core import WaterMark
from .exceptions import WatermarkError

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 使用說明
USAGE_EMBED = 'blind_watermark --embed --pwd 1234 image.jpg "watermark text" embed.png'
USAGE_EXTRACT = 'blind_watermark --extract --pwd 1234 --wm_shape 111 embed.png'

# 創建選項解析器
opt_parser = OptionParser(usage=USAGE_EMBED + '\n' + USAGE_EXTRACT)

opt_parser.add_option(
    '--embed',
    dest='work_mode',
    action='store_const',
    const='embed',
    help='嵌入水印到圖片'
)
opt_parser.add_option(
    '--extract',
    dest='work_mode',
    action='store_const',
    const='extract',
    help='從圖片提取水印'
)
opt_parser.add_option(
    '-p', '--pwd',
    dest='password',
    help='密碼，例如 1234'
)
opt_parser.add_option(
    '--wm_shape',
    dest='wm_shape',
    help='水印形狀，例如 120'
)


def main() -> Optional[int]:
    """
    主函數

    Returns:
        退出碼（0 表示成功，1 表示失敗）
    """
    opts, args = opt_parser.parse_args()

    try:
        # 檢查密碼
        if not opts.password:
            logger.error("必須提供密碼參數 --pwd")
            return 1

        password = int(opts.password)
        bwm = WaterMark(password_img=password, password_wm=password)

        if opts.work_mode == 'embed':
            return handle_embed(bwm, args)
        elif opts.work_mode == 'extract':
            return handle_extract(bwm, args, opts)
        else:
            logger.error("必須指定 --embed 或 --extract")
            opt_parser.print_help()
            return 1

    except WatermarkError as e:
        logger.error(f"水印處理錯誤: {e}")
        return 1
    except Exception as e:
        logger.error(f"未預期的錯誤: {e}")
        return 1


def handle_embed(bwm: WaterMark, args: list) -> int:
    """
    處理嵌入操作

    Args:
        bwm: WaterMark 實例
        args: 命令列參數

    Returns:
        退出碼
    """
    if len(args) != 3:
        logger.error(f"嵌入模式需要 3 個參數\n使用方式: {USAGE_EMBED}")
        return 1

    input_file, watermark_text, output_file = args

    logger.info(f"讀取圖片: {input_file}")
    bwm.read_img(input_file)

    logger.info(f"讀取水印: {watermark_text}")
    bwm.read_wm(watermark_text, mode='str')

    logger.info(f"嵌入水印...")
    bwm.embed(output_file)

    logger.info(f"成功！輸出檔案: {output_file}")
    logger.info(f"水印位元長度: {len(bwm.wm_bit)}")

    return 0


def handle_extract(bwm: WaterMark, args: list, opts) -> int:
    """
    處理提取操作

    Args:
        bwm: WaterMark 實例
        args: 命令列參數
        opts: 選項物件

    Returns:
        退出碼
    """
    if len(args) != 1:
        logger.error(f"提取模式需要 1 個參數\n使用方式: {USAGE_EXTRACT}")
        return 1

    if not opts.wm_shape:
        logger.error("提取模式必須提供 --wm_shape 參數")
        return 1

    input_file = args[0]
    wm_shape = int(opts.wm_shape)

    logger.info(f"從圖片提取水印: {input_file}")
    wm_str = bwm.extract(filename=input_file, wm_shape=wm_shape, mode='str')

    logger.info("提取成功！")
    print(f"\n水印內容: {wm_str}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
