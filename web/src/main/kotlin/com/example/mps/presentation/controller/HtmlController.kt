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
    fun index(model: Model, @RequestParam(defaultValue = "1") page: Int): String {
        return if (page >= 1) {
            val pageData = service.getMatches(page - 1).map { MatchView.fromMatch(it) }
            model["title"] = "Mps"
            model["page"] = page
            model["totalPages"] = pageData.totalPages
            model["matches"] = pageData.content
            "index"
        } else {
            "404"
        }
    }
}