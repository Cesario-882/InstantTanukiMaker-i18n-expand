import wx
import threading

from config import CONFIG
import dialogs
import editor
import wxlib
from i18n import _


class MenuBar(wx.MenuBar):
    def __init__(self):
        super().__init__()
        menu_file, menu_edit = wx.Menu(), wx.Menu()

        # ファイル
        menu_save = menu_file.Append(-1, _("プロジェクト保存"), _("現在の作業状況をpkl形式で保存します。"))
        menu_load = menu_file.Append(-1, _("プロジェクト読込"), _("pkl形式のファイルから作業状況を読み込みます。"))
        # 画像加工
        menu_convert = menu_edit.Append(-1, _("アニメーションコンバータ"), _("アニメーション画像の作成、分解ができます。"))
        # menu_transparent = menu_edit.Append(-1, _("透過画像追加"), _("選択した色を透過して一覧に追加します。"))

        self.Append(menu_file, _("ファイル"))
        self.Append(menu_edit, _("画像加工"))

        self.Bind(wx.EVT_MENU, self.on_save, menu_save)
        self.Bind(wx.EVT_MENU, self.on_load, menu_load)
        self.Bind(wx.EVT_MENU, self.on_convert, menu_convert)
        # self.Bind(wx.EVT_MENU, self.on_transparent, menu_transparent)

    def on_save(self, event):
        path_save = wxlib.save_file(None, _("プロジェクト保存"), "*.json", _("たぬこらプロジェクト.json"))
        if not path_save:
            return

        wxlib.post_start_progress(self.GetParent(), "少しお待ちください…", _("プロジェクト保存中"))
        thread_save = threading.Thread(target=self.save, args=(path_save,))
        thread_save.start()

    def save(self, path_save):
        with wxlib.progress_context(self.GetParent(), _("保存に失敗しました…"), _("プロジェクト保存失敗")):
            CONFIG.save_manager(path_save)
            message = _("保存が完了しました！")
            caption = _("プロジェクト保存完了")
            style = wx.ICON_INFORMATION
            wxlib.post_end_progress(self.GetParent(), message, caption, style, path_save.parent)

    def on_load(self, event):
        message = _("プロジェクトを読み込むと現在の作業状況は失われます！")
        caption = _("読込前の注意")
        wxlib.show_message(None, message, caption, wx.ICON_EXCLAMATION)
        path_json = wxlib.select_file(None, _("プロジェクト読込"), "*.json")
        if not path_json:
            return

        wxlib.post_start_progress(self.GetParent(), "少しお待ちください…", _("プロジェクト読込中"))
        thread_load = threading.Thread(target=self.load, args=(path_json,))
        thread_load.start()

    def load(self, path_json):
        with wxlib.progress_context(self.GetParent(), _("プロジェクトの読み込みに失敗しました..."), _("プロジェクト読込失敗")):
            is_completed, message = CONFIG.load_manager(path_json)
            if is_completed:
                wxlib.post_update(self.GetParent(), True, True, True, reset=True)

            caption = "プロジェクト読込完了" if is_completed else _("プロジェクト読込失敗")
            style = wx.ICON_INFORMATION if is_completed else wx.ICON_ERROR
            wxlib.post_end_progress(self.GetParent(), message, caption, style)

    def on_convert(self, event):
        with dialogs.AnimationConverterDialog(self.GetParent()) as dial:
            dial.ShowModal()

    def on_transparent(self, event):
        with dialogs.ImageSelectDialog(self.GetParent(), _("透過したい画像を選択")) as dial:
            result = dial.ShowModal()
            if result != wx.ID_OK:
                return

            path_image, frames, id_replace = dial.get_select_image()

        with dialogs.SelectColorDialog(self.GetParent(), path_image, frames) as dial:
            result = dial.ShowModal()
            if result != wx.ID_OK:
                return

            colors_target, is_face = dial.get_colors_target()

        wxlib.post_start_progress(self.GetParent(), _("しばらくお待ちください…"), _("透過画像作成中"))
        thread = threading.Thread(target=self.create_transparent,
                                  args=(path_image, frames, colors_target, is_face, id_replace))
        thread.start()

    def create_transparent(self, path_image, frames, colors_target, is_face, id_replace):
        with wxlib.progress_context(self.GetParent(), _("透過画像の作成に失敗しました…"), _("透過画像作成失敗")):
            frames = frames if frames else editor.get_frames(path_image)
            if not frames:
                message = _("{name}が開けません!").format(name=path_image.stem)
                caption = _("ファイルアクセスエラー")
                style = wx.ICON_ERROR
                wxlib.post_end_progress(self.GetParent(), message, caption, style=style)
                return

            frames = editor.make_transparent(frames, colors_target, is_face)
            if frames:
                path_image = path_image.parent / f"{path_image.stem}【透過】{path_image.suffix}"
                wxlib.post_append(self.GetParent(), path_image, frames, id_replace)

            caption = _("透過画像作成完了") if frames else _("透過画像作成失敗")
            message = _("透過画像の作成が完了しました!") if frames else _("透過画像の作成に失敗しました…")
            style = wx.ICON_INFORMATION if frames else wx.ICON_ERROR
            wxlib.post_end_progress(self.GetParent(), message, caption, style=style)

    def on_costume(self, event):
        with dialogs.ImageSelectDialog(self.GetParent(), _("きぐるみ用に顔を切り抜きたい画像を選択")) as dial:
            result = dial.ShowModal()
            if result != wx.ID_OK:
                return

            path_image, frames, id_replace = dial.get_select_image()

        wxlib.post_start_progress(self.GetParent(), _("しばらくお待ちください…"), _("きぐるみ顔切り抜き"))
        thread = threading.Thread(target=self.clip_for_costume,
                                  args=(path_image, frames, id_replace))
        thread.start()

    def clip_for_costume(self, path_image, frames, id_replace):
        frames = frames if frames else editor.get_frames(path_image)
        if not frames:
            message = _("{name}が開けません!").format(name=path_image.stem)
            caption = _("ファイルアクセスエラー")
            style = wx.ICON_ERROR
            wxlib.post_end_progress(self.GetParent(), message=message, caption=caption, style=style)
            return

        frames = editor.clip_for_costume(path_image, frames)
        if frames:
            path_image = path_image.parent / f"{path_image.stem}【きぐるみ】{path_image.suffix}"
            wxlib.post_append(self.GetParent(), path_image, frames, id_replace)

        caption = _("きぐるみ完了") if frames else _("きぐるみ失敗")
        message = _("きぐるみの作成が完了しました!") if frames else _("きぐるみの作成に失敗しました…")
        style = wx.ICON_INFORMATION if frames else wx.ICON_ERROR
        wxlib.post_end_progress(self.GetParent(), message=message, caption=caption, style=style)


class AppendMenu(wx.Menu):
    def __init__(self, parent, path, frames, id_replace):
        super().__init__()
        self.parent = parent
        self.path = path
        self.frames = frames
        self.id_replace = id_replace
        self.target_post = parent.GetTopLevelParent()

        menu_transparent = self.Append(-1, _("透過画像の追加"), _("選択した色を透過して一覧に追加します。"))
        self.Bind(wx.EVT_MENU, self.on_transparent, menu_transparent)
        if not frames:
            self.AppendSeparator()
            menu_separate = self.Append(-1, _("フレーム分割"), _("フレームごとに分割して画像追加パネルに表示します。"))
            menu_costume = self.Append(-1, _("きぐるみ切り抜き"), _("きぐるみ用に顔の部分だけ切り抜いて一覧に追加します。"))
            self.Bind(wx.EVT_MENU, self.on_separate, menu_separate)
            self.Bind(wx.EVT_MENU, self.on_costume, menu_costume)

        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.on_highlight)
        self.Bind(wx.EVT_MENU_CLOSE, self.on_close)

    def on_separate(self, event):
        im = editor.open_image(self.path)
        if not im:
            message = _("{name}が開けません！").format(name=self.path.name)
            caption = _("ファイルアクセスエラー")
            style = wx.ICON_ERROR
            wxlib.post_info(self.parent.GetTopLevelParent(), message, caption, style)
            return

        if not getattr(im, "is_animated", False):
            return

        wxlib.post_select(self.parent, self.path)

    def on_transparent(self, event):
        with dialogs.SelectColorDialog(self.parent, self.path, self.frames) as dial:
            result = dial.ShowModal()
            if result != wx.ID_OK:
                return

            colors_target, face_only = dial.get_colors_target()

        if not colors_target:
            return

        wxlib.post_start_progress(self.parent.GetTopLevelParent(), _("しばらくお待ちください…"), _("透過画像作成中"))
        args = (self.path, self.frames, colors_target, face_only, self.id_replace)
        thread = threading.Thread(target=self.create_transparent, args=args)
        thread.start()

    def create_transparent(self, path_image, frames, colors_target, is_face, id_replace):
        with wxlib.progress_context(self.target_post, _("透過画像の作成に失敗しました…"), _("透過画像作成失敗")):
            frames = frames if frames else editor.get_frames(path_image)
            if not frames:
                message = _("{name}が開けません!").format(name=path_image.stem)
                caption = _("ファイルアクセスエラー")
                style = wx.ICON_ERROR
                wxlib.post_end_progress(self.target_post, message=message, caption=caption,
                                        style=style)
                return

            frames = editor.make_transparent(frames, colors_target, is_face)
            if frames:
                path_image = path_image.parent / f"{path_image.stem}【透過】{path_image.suffix}"
                wxlib.post_append(self.target_post, path_image, frames, id_replace)

            caption = _("透過画像作成完了") if frames else _("透過画像作成失敗")
            message = _("透過画像の作成が完了しました!") if frames else _("透過画像の作成に失敗しました…")
            style = wx.ICON_INFORMATION if frames else wx.ICON_ERROR
            wxlib.post_end_progress(self.target_post, message=message, caption=caption, style=style)

    def on_costume(self, event):
        wxlib.post_start_progress(self.parent.GetTopLevelParent(), _("しばらくお待ちください…"), _("きぐるみ顔切り抜き"))
        thread = threading.Thread(target=self.clip_for_costume,
                                  args=(self.path, self.frames, self.id_replace))
        thread.start()

    def clip_for_costume(self, path_image, frames, id_replace):
        with wxlib.progress_context(self.target_post, _("切り抜きに失敗しました…"), _("切り抜き失敗")):
            frames = frames if frames else editor.get_frames(path_image)
            if not frames:
                message = _("{name}が開けません!").format(name=path_image.stem)
                caption = _("ファイルアクセスエラー")
                style = wx.ICON_ERROR
                wxlib.post_end_progress(self.target_post, message=message, caption=caption,
                                        style=style)
                return

            frames = editor.clip_for_costume(path_image, frames)
            if frames:
                path_image = path_image.parent / f"{path_image.stem}【きぐるみ】{path_image.suffix}"
                wxlib.post_append(self.target_post, path_image, frames, id_replace)

            caption = _("切り抜き完了") if frames else _("切り抜き失敗")
            message = _("きぐるみ切り抜きが完了しました!") if frames else _("きぐるみ切り抜きに失敗しました…")
            style = wx.ICON_INFORMATION if frames else wx.ICON_ERROR
            wxlib.post_end_progress(self.target_post, message=message, caption=caption, style=style)

    def on_highlight(self, event):
        helpstring = self.GetHelpString(event.GetMenuId())
        if helpstring:
            self.target_post.DoGiveHelp(helpstring, True)

    def on_close(self, event):
        self.target_post.DoGiveHelp("", False)


class ComponentMenu(wx.Menu):
    def __init__(self, parent, id_image):
        super().__init__()
        self.parent = parent
        self.id_image = id_image

        menu_replace = self.Append(-1, _("交換"), _("プロパティを引き継いで画像を交換する"))
        menu_clipper = self.Append(-1, _("クリッパー設定"), _("画像と重なった部分を切り取るクリッパーを設定する。"))
        self.Bind(wx.EVT_MENU, self.on_replace, menu_replace)
        self.Bind(wx.EVT_MENU, self.on_clipper, menu_clipper)

        if CONFIG.manager.is_file(self.id_image):
            self.AppendSeparator()
            menu_remove = self.Append(-1, _("削除"), _("画像を削除する"))
            self.Bind(wx.EVT_MENU, self.on_remove, menu_remove)

        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.on_highlight)
        self.Bind(wx.EVT_MENU_CLOSE, self.on_close)

    def on_replace(self, event):
        with dialogs.ImageSelectDialog(self.parent, _("画像交換ダイアログ"), self.id_image) as dial:
            result = dial.ShowModal()
            if result != wx.ID_OK:
                return

            path_image, frames, id_replace = dial.get_select_image()
            wxlib.post_append(self.parent, path_image, frames, id_replace)

    def on_clipper(self, event):
        with dialogs.ClipperSelectDialog(self.parent, self.id_image) as dial:
            dial.ShowModal()

    def on_remove(self, event):
        CONFIG.manager.remove(self.id_image)
        wxlib.post_update(self.parent, True, True, True)

    def on_highlight(self, event):
        helpstring = self.GetHelpString(event.GetMenuId())
        if helpstring:
            self.parent.DoGiveHelp(helpstring, True)

    def on_close(self, event):
        self.parent.DoGiveHelp("", False)
