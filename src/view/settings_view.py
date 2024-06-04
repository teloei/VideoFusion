from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget
from qfluentwidgets import (BodyLabel, ComboBoxSettingCard, FluentIcon, Icon, PushSettingCard, RangeSettingCard,
                            SettingCardGroup, SwitchSettingCard, ToolTipFilter)
from qfluentwidgets.components import (
    ExpandLayout,
    LargeTitleLabel,
    SmoothScrollArea,
    )

import resource_rc  # noqa: F401
from src.config import cfg
from src.core.version import __version__
from src.view.message_base_view import MessageBaseView


class SettingView(MessageBaseView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("setting_view")
        self.main_layout = QVBoxLayout()
        self.smooth_scroll_area = SmoothScrollArea()

        # 这里是一个补丁,因为不知道为什么MessageBaseView没有调用父类的构造函数
        # 所以这里手动初始化一下
        self.is_state_tooltip_running: bool = False

        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.setting_title = LargeTitleLabel()
        self.setting_title.setText("设置")

        self.version_lb: BodyLabel = BodyLabel()
        self.version_lb.setText(f'当前软件版本: {__version__}')
        self.version_lb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._create_card_group()
        self._create_card()
        self._set_up_tooltip()
        self._set_up_layout()
        self._initialize()

    def _create_card_group(self):
        self.video_group = SettingCardGroup("视频", self.scroll_widget)
        self.general_group = SettingCardGroup("通用", self.scroll_widget)

    def _create_card(self):
        # 全局设置
        self.ffmpeg_file_card = PushSettingCard("FFmpeg路径", Icon(FluentIcon.CHEVRON_RIGHT), "设置FFmpeg的路径",
                                                "您可以选择您自己编译的ffmpeg.exe,该软件仅使用了基础的ffmpeg,可能对某些视频格式不支持",
                                                self.general_group)
        self.temp_dir_card = PushSettingCard("选择目录", Icon(FluentIcon.CHEVRON_RIGHT), "设置临时目录",
                                             "软件在运行的过程中会产生过程文件，请确保目标目录有足够的空间",
                                             self.general_group)
        self.delete_temp_dir_card = SwitchSettingCard(Icon(FluentIcon.CHEVRON_RIGHT), "删除临时目录",
                                                      "软件在完成后是否删除临时目录", cfg.delete_temp_dir,
                                                      self.general_group)
        self.preview_video_remove_black_card = SwitchSettingCard(Icon(FluentIcon.CHEVRON_RIGHT), "预览视频去黑边",
                                                                 "最终拼接合成的视频不一定和去黑边一样,拼接的结果是多个帧优化之后的结果,单张图片效果不是很好",
                                                                 cfg.preview_video_remove_black,
                                                                 self.general_group)
        self.preview_frame_card = ComboBoxSettingCard(cfg.preview_frame, Icon(FluentIcon.CHEVRON_RIGHT), "预览视频帧",
                                                      "设置预览视频的封面为第几帧的图片",
                                                      ["第一帧", "最后一帧", "随机帧"], self.general_group)

        # 视频质量
        self.output_file_path_card = PushSettingCard("输出文件路径", Icon(FluentIcon.CHEVRON_RIGHT), "设置输出文件路径",
                                                     "设置输出文件路径", self.video_group)
        self.deband_card = SwitchSettingCard(Icon(FluentIcon.CHEVRON_RIGHT), "视频去色带",
                                             "色带是指画面中出现的一种颜色条纹,如果视频本身画面有色带,请尝试勾选此选项,否则可能会导致画面失真",
                                             cfg.deband, self.video_group)
        self.deblock_card = SwitchSettingCard(Icon(FluentIcon.CHEVRON_RIGHT), "视频去色块",
                                              "色块是指画面中出现的一种颜色块,如果视频本身画面有色块,请尝试勾选此选项,否则可能会导致画面失真",
                                              cfg.deblock, self.video_group)
        self.shake_card = SwitchSettingCard(Icon(FluentIcon.CHEVRON_RIGHT), "视频去抖动",
                                            "如果视频本身视角转动过快会导致画面大幅无规律异常抖动,请谨慎使用",
                                            cfg.shake, self.video_group)
        self.video_fps_card = RangeSettingCard(cfg.video_fps, Icon(FluentIcon.CHEVRON_RIGHT), "输出视频帧率",
                                               "调整输出视频的帧率,默认为30fps", self.video_group)
        self.video_sample_rate_card = RangeSettingCard(cfg.video_sample_rate, Icon(FluentIcon.CHEVRON_RIGHT),
                                                       "去黑边采样率",
                                                       "通过算法去除视频的黑边或者logo等,留下视频的主体画面",
                                                       self.video_group)
        self.audio_normalization_card = ComboBoxSettingCard(cfg.audio_normalization, Icon(FluentIcon.CHEVRON_RIGHT),
                                                            "视频音量自动调整",
                                                            "将声音过大或者过小的视频音频自动调整到合适的响度",
                                                            ["关闭", "电台(嘈杂环境)", "TV(普通环境)",
                                                                    "电影(安静环境)"],
                                                            self.video_group)
        self.audio_noise_reduction_card = ComboBoxSettingCard(cfg.audio_noise_reduction, Icon(FluentIcon.CHEVRON_RIGHT),
                                                              "音频降噪",
                                                              "降低音频中的底噪,杂音,爆音等异常声音",
                                                              ["关闭", "静态分析(速度快)", "AI模型分析(效果好)"],
                                                              self.video_group)
        self.video_noise_reduction_card = ComboBoxSettingCard(cfg.video_noise_reduction, Icon(FluentIcon.CHEVRON_RIGHT),
                                                              "视频降噪",
                                                              "降低视频中的噪点,杂点,闪缩的各种异常杂斑等异常画面",
                                                              ["关闭", "hqdn3d(快速降噪)", "nlmeans(效果好,速度慢)"],
                                                              self.video_group)
        self.scaling_quality_card = ComboBoxSettingCard(cfg.scaling_quality, Icon(FluentIcon.CHEVRON_RIGHT),
                                                        "分辨率缩放算法",
                                                        "调整视频分辨率的时候使用的算法",
                                                        ["nearest可能会出现锯齿和块状伪影,图像质量不高",
                                                                "bilinear可能会出现模糊,不适合细节要求高的场景",
                                                                'bicubic计算量较大,图像质量较好,适合大多数场景',
                                                                "lanczos计算量大,速度很慢,图像质量很高",
                                                                "sinc计算量极大,图像质量最高"
                                                                ],
                                                        self.video_group)
        self.rate_adjustment_type_card = ComboBoxSettingCard(cfg.rate_adjustment_type, Icon(FluentIcon.CHEVRON_RIGHT),
                                                             "视频补帧算法",
                                                             "调整视频帧率的算法",
                                                             ["普通补帧", "光流法补帧(效果好速度慢)"],
                                                             self.video_group)
        self.output_codec_card = ComboBoxSettingCard(cfg.output_codec, Icon(FluentIcon.CHEVRON_RIGHT), "输出视频编码",
                                                     "调整视频编码的算法",
                                                     ["H264", "H264Intel", "H264AMD", "H264Nvidia",
                                                             "H265", "H265Intel", "H265AMD", "H265Nvidia"],
                                                     self.video_group)

    def _set_up_tooltip(self):
        ffmpeg_file_path = cfg.get(cfg.ffmpeg_file)
        self.ffmpeg_file_card.setToolTip(f'当前FFmpeg路径为: {ffmpeg_file_path}')
        temp_dir_path = cfg.get(cfg.temp_dir)
        self.temp_dir_card.setToolTip(f'当前临时目录为: {temp_dir_path}')
        self.delete_temp_dir_card.setToolTip(
                "软件在完成后是否删除临时目录(软件退出之后才会删除,该方法删除的文件无法恢复)")
        self.preview_video_remove_black_card.setToolTip(
                "如果您发现您的画面黑边,请尝试勾选此选项,但是单帧画面效果不是很好,请通过预览视频查看效果")
        self.preview_frame_card.setToolTip("设置预览视频的封面为第几帧的图片")

        output_file_path = cfg.get(cfg.output_file_path)
        self.output_file_path_card.setToolTip(f'当前输出文件路径为: {output_file_path}')
        self.audio_noise_reduction_card.setToolTip(
                "降低音频中的底噪,杂音,爆音等异常声音,建议使用AI模型分析,速度快效果好")
        self.video_noise_reduction_card.setToolTip(
                "请注意nlmeans速度非常慢,开始和结束都会有一段时间进度条为0,请耐心等待,如果日志持续在输出则表示没有卡死")
        self.audio_normalization_card.setToolTip("小概率会出现音频爆响")
        self.deband_card.setToolTip(
                '<html><head/><body><p><img src=":/tooltip/images/tooltip/debanding.png"/></p></body></html>')
        self.deblock_card.setToolTip(
            '<html><head/><body><p><img src=":/tooltip/images/tooltip/Deblocking.png"/></p></body></html>')
        self.shake_card.setToolTip("实验性功能")
        self.video_fps_card.setToolTip(
                "调整输出视频的帧率,默认为30fps,帧率距离原始视频帧率过高或者过低都有可能出现未知的异常")
        self.video_sample_rate_card.setToolTip(
            '<html><head/><body><p><img src=":/tooltip/images/tooltip/black_remover.png"/>'
            '</p><p>值为0则不启用去除黑边,0~1之间使用静态去黑边,为1则开启动态去黑边模式</p></body></html>')
        self.scaling_quality_card.setToolTip(
            '<html><head/><body><p><img src=":/tooltip/images/tooltip/upscale.png"/></p></body></html>')
        self.rate_adjustment_type_card.setToolTip("调整视频帧率的算法,光流法会大幅增加运算时间")
        self.output_codec_card.setToolTip(
            "调整视频编码的算法,默认推荐经过优化的H264算法,压缩比例非常高,且画质清晰,适合大部分场景")

    def _set_up_layout(self):
        """设置布局"""
        self.smooth_scroll_area.setWidget(self.scroll_widget)

        self.expand_layout.addWidget(self.general_group)
        self.expand_layout.addWidget(self.video_group)
        self.scroll_widget.setLayout(self.expand_layout)
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)

        # 给卡片组添加卡片
        self.general_group.addSettingCards([
                self.ffmpeg_file_card,
                self.temp_dir_card,
                self.delete_temp_dir_card,
                self.preview_video_remove_black_card,
                self.preview_frame_card
                ])
        self.video_group.addSettingCards([
                self.output_file_path_card,
                self.deband_card,
                self.deblock_card,
                self.shake_card,
                self.video_fps_card,
                self.video_sample_rate_card,
                self.audio_normalization_card,
                self.audio_noise_reduction_card,
                self.video_noise_reduction_card,
                self.scaling_quality_card,
                self.rate_adjustment_type_card,
                self.output_codec_card,
                ])

    def _initialize(self) -> None:
        """初始化窗体"""
        self.setWindowTitle("设置")
        self.setObjectName("setting_view")
        self.resize(1100, 800)
        self.smooth_scroll_area.setWidgetResizable(True)
        self.smooth_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.setting_title.setMargin(30)
        self.setting_title.setFixedWidth(200)

        self.main_layout.addWidget(self.setting_title)
        self.main_layout.addWidget(self.smooth_scroll_area)
        self.main_layout.addWidget(self.version_lb)
        self.setLayout(self.main_layout)

        # 这里因为背景色不一样,我手动打个补丁
        self.setStyleSheet("background-color: #f9f9f9")
        self.smooth_scroll_area.setStyleSheet("background-color: #f9f9f9")

        for each in self.findChildren(QWidget):
            each.installEventFilter(ToolTipFilter(each, 200))


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    s = SettingView()
    s.show()
    app.exec()
