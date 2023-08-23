package com.example.mps.presentation.controller

import com.example.mps.presentation.model.MatchView
import com.example.mps.persistence.service.MatchService
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.ui.set
import org.springframework.web.bind.annotation.GetMapping


@Controller
class HtmlController(
    private val service: MatchService
) {

    @GetMapping("/")
    fun index(model: Model): String {
        model["title"] = "Mps"
        model["matches"] = service.getMatches().map { MatchView.fromMatch(it)}
        return "index"
    }
}