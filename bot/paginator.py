from disnake import ui, ButtonStyle, MessageInteraction


class PreviousButton(ui.Button):
    def __init__(self, disabled ):
        super().__init__(
            emoji="⬅️",
            style=ButtonStyle.grey,
            disabled=disabled,
            custom_id='previous'
        )

    async def callback(self, inter: MessageInteraction) -> None:
        view: PaginatorView = self.view
        try:
            if view.page:
                await inter.response.defer()
                view.page -= 1
                page = view.get_page(view.page)
                view.count = page["count"]

                if view.page == 0:
                    self.disabled = True
                for btn in view.children:
                    if btn.custom_id == "next":
                        btn.disabled = False
                await inter.edit_original_message(embed=page["embed"], view=view)
                
        except:
            await inter.send('Unable to change the page.', ephemeral=True)


class NextButton(ui.Button):
    def __init__(self, disabled):
        super().__init__(
            emoji="➡️",
            style=ButtonStyle.grey,
            disabled=disabled,
            custom_id='next'
        )

    async def callback(self, inter: MessageInteraction) -> None:
        view: PaginatorView = self.view
        try:
            await inter.response.defer()
            view.page += 1
            page = view.get_page(view.page)
            view.count = page["count"]

            if view.page == (view.count-1) // view.limit:
                self.disabled = True
            for btn in view.children:
                if btn.custom_id == "previous":
                    btn.disabled = False
            await inter.edit_original_message(embed=page["embed"], view=view)
            
        except:
            await inter.send('Unable to change the page.', ephemeral=True)


class PaginatorView(ui.View):
    def __init__(self, get_page, page_size, count):
        super().__init__()
        self.get_page = get_page
        self.page = 0
        self.count = count
        self.limit = page_size
        if self.count > self.limit:
            self.add_item(PreviousButton(True))
            self.add_item(NextButton(False))