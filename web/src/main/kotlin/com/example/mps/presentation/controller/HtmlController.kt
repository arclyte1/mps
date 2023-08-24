package com.example.mps.presentation.controller

import com.example.mps.presentation.model.MatchView
import com.example.mps.persistence.service.MatchService
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.ui.set
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestParam


@Controller
class HtmlController(
    private val service: MatchService
) {

    @GetMapping("/")
    fun index(model: Model, @RequestParam(defaultValue = "0") page: Int): String {
        val pageData = service.getMatches(page).map { MatchView.fromMatch(it) }
        model["title"] = "Mps"
        model["page"] = page
        model["pageCount"] = pageData.totalPages
        model["matches"] = pageData.content
        return "index"
    }
}