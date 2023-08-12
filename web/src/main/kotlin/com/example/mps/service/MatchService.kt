package com.example.mps.service

import com.example.mps.model.Match
import com.example.mps.model.MatchView
import com.example.mps.repository.MatchRepository
import org.springframework.stereotype.Service

@Service
class MatchService(
    private val repository: MatchRepository
) {

    fun getMatches(): List<Match> {
        return repository.findAll().map { it.toMatch() }
    }
}