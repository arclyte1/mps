package com.example.mps.model

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Table


@Entity
@Table(name = "match")
data class MatchEntity(

    @Id
    @Column(name = "id")
    val id: Long,

    @Column(name = "name")
    val name: String?,
) {

    fun toMatch(): Match {
        return Match(
            id = id,
            name = name,
        )
    }
}
